from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db.models import Avg, Count
from django.http import Http404
from .forms import ProductForm
from .models import Product, Review
from orders.models import OrderItem


@login_required
def create_listing(request):
    if not getattr(request.user, 'is_seller', False):
        messages.error(request, 'Only sellers can create listings.')
        return redirect('home')
        
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            # is_approved defaults to False
            product.save()
            messages.success(request, 'Listing created successfully! It will be visible once approved by an admin.')
            return redirect('home')
    else:
        form = ProductForm()
        
    return render(request, 'listings/create_listing.html', {'form': form})


def product_detail(request, product_id):
    """Render full product details with product-specific reviews."""
    product = get_object_or_404(Product.objects.select_related('seller'), id=product_id)

    is_owner = request.user.is_authenticated and request.user == product.seller
    if not is_owner and (not product.is_approved or not product.seller.is_active):
        raise Http404("This product is not available.")

    reviews = product.reviews.select_related('buyer').all()
    review_stats = reviews.aggregate(avg_rating=Avg('rating'), review_count=Count('id'))
    avg_rating = round(review_stats['avg_rating'] or 0, 1)
    review_count = review_stats['review_count'] or 0

    rounded_to_half = round(avg_rating * 2) / 2
    star_display = []
    for i in range(1, 6):
        if rounded_to_half >= i:
            star_display.append('full')
        elif rounded_to_half >= (i - 0.5):
            star_display.append('half')
        else:
            star_display.append('empty')

    can_review = False
    has_reviewed = False
    if request.user.is_authenticated and getattr(request.user, 'is_buyer', False):
        has_purchased = OrderItem.objects.filter(
            order__buyer=request.user,
            product=product,
        ).exists()
        has_reviewed = Review.objects.filter(product=product, buyer=request.user).exists()
        can_review = has_purchased and not has_reviewed

    return render(request, 'listings/product_detail.html', {
        'product': product,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'review_count': review_count,
        'star_display': star_display,
        'is_owner': is_owner,
        'can_review': can_review,
        'has_reviewed': has_reviewed,
    })


def product_quickview(request, product_id):
    """Return partial HTML for the quickview modal with product details and reviews."""
    product = get_object_or_404(Product, id=product_id)

    # Only the seller of the product can view unapproved / inactive-seller products
    is_owner = request.user.is_authenticated and request.user == product.seller
    if not is_owner:
        if not product.is_approved or not product.seller.is_active:
            from django.http import HttpResponseForbidden
            return HttpResponseForbidden("This product is not available.")

    reviews = product.reviews.select_related('buyer').all()
    review_stats = reviews.aggregate(avg_rating=Avg('rating'), review_count=Count('id'))
    avg_rating = review_stats['avg_rating'] or 0
    review_count = review_stats['review_count']

    context = {
        'product': product,
        'reviews': reviews,
        'avg_rating': round(avg_rating, 1),
        'review_count': review_count,
        'is_owner': is_owner,
    }
    return render(request, 'listings/quickview.html', context)


@login_required
@require_POST
def submit_review(request, product_id):
    """Submit a review for a product (buyers only, must have purchased)."""
    product = get_object_or_404(Product, id=product_id, is_approved=True)

    if not getattr(request.user, 'is_buyer', False):
        messages.error(request, 'Only buyers can leave reviews.')
        return redirect('purchase_history')

    # Check if already reviewed
    if Review.objects.filter(product=product, buyer=request.user).exists():
        messages.warning(request, 'You have already reviewed this product.')
        return redirect('purchase_history')

    # Check if user purchased this product
    has_purchased = OrderItem.objects.filter(
        order__buyer=request.user,
        product=product,
    ).exists()
    if not has_purchased:
        messages.error(request, 'You can only review products you have purchased.')
        return redirect('purchase_history')

    # Validate rating
    try:
        rating = int(request.POST.get('rating', 0))
        if rating < 1 or rating > 5:
            raise ValueError
    except (ValueError, TypeError):
        messages.error(request, 'Please select a rating between 1 and 5.')
        return redirect('purchase_history')

    comment = request.POST.get('comment', '').strip()
    if not comment:
        messages.error(request, 'Please write a comment for your review.')
        return redirect('purchase_history')

    Review.objects.create(
        product=product,
        buyer=request.user,
        rating=rating,
        comment=comment,
    )
    messages.success(request, 'Your review has been submitted!')
    return redirect('purchase_history')


@login_required
def seller_reviews(request):
    """Show all reviews for the logged-in seller's products."""
    if not getattr(request.user, 'is_seller', False):
        return redirect('home')

    reviews = (
        Review.objects.filter(product__seller=request.user)
        .select_related('product', 'buyer')
        .order_by('-created_at')
    )

    # Aggregate stats across all seller products
    stats = reviews.aggregate(avg_rating=Avg('rating'), total_count=Count('id'))

    context = {
        'reviews': reviews,
        'avg_rating': round(stats['avg_rating'] or 0, 1),
        'total_count': stats['total_count'],
    }
    return render(request, 'listings/seller_reviews.html', context)


def search_products_ajax(request):
    """Return partial HTML containing filtered product cards."""
    q = request.GET.get('q', '').strip()
    
    # We apply the same general constraint that only approved items are shown.
    base_query = Product.objects.filter(is_approved=True, seller__is_active=True)
    
    if q:
        from django.db.models import Q
        products = base_query.filter(
            Q(name__icontains=q) | Q(description__icontains=q)
        ).order_by('-id')
    else:
        products = base_query.order_by('-id')

    return render(request, 'listings/product_grid_items.html', {
        'products': products,
        'is_seller_view': False
    })


@require_POST
def add_to_compare(request, product_id):
    """Add a product to the comparison list in the session."""
    if 'compare_list' not in request.session:
        request.session['compare_list'] = []
    
    compare_list = request.session['compare_list']
    
    if product_id not in compare_list:
        if len(compare_list) >= 3:
            messages.warning(request, "You can only compare up to 3 products at a time.")
        else:
            compare_list.append(product_id)
            request.session.modified = True
            messages.success(request, "Product added to compare list.")
    else:
        messages.info(request, "Product is already in your compare list.")
        
    return redirect(request.META.get('HTTP_REFERER', 'home'))


@require_POST
def remove_from_compare(request, product_id):
    """Remove a product from the comparison list."""
    if 'compare_list' in request.session:
        compare_list = request.session['compare_list']
        if product_id in compare_list:
            compare_list.remove(product_id)
            request.session.modified = True
            messages.success(request, "Product removed from compare list.")
            
    return redirect('compare_products')


def compare_products(request):
    """Render the comparison page with selected products."""
    compare_list = request.session.get('compare_list', [])
    products = Product.objects.filter(id__in=compare_list)
    
    return render(request, 'listings/compare.html', {
        'products': products
    })
