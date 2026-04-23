from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from listings.models import Product
from users.models import User
from .decorators import admin_required


@admin_required
def admin_dashboard(request):
    """
    Admin dashboard showing key statistics and recent activities
    """
    stats = {
        'total_users': User.objects.filter(role__in=['buyer', 'seller']).count(),
        'total_sellers': User.objects.filter(role='seller', is_active=True).count(),
        'total_buyers': User.objects.filter(role='buyer', is_active=True).count(),
        'total_products': Product.objects.count(),
        'approved_products': Product.objects.filter(is_approved=True).count(),
        'pending_products': Product.objects.filter(is_approved=False, is_rejected=False).count(),
        'pending_users': User.objects.filter(is_approved=False, role__in=['buyer', 'seller']).count(),
        'banned_users': User.objects.filter(is_active=False, role__in=['buyer', 'seller']).count(),
    }
    
    # Get recent pending products and users
    recent_pending = Product.objects.filter(is_approved=False, is_rejected=False).select_related('seller').order_by('-id')[:5]
    recent_pending_users = User.objects.filter(is_approved=False, role__in=['buyer', 'seller']).order_by('-id')[:5]
    
    context = {
        'stats': stats,
        'recent_pending': recent_pending,
        'recent_pending_users': recent_pending_users,
    }
    return render(request, 'admin_panel/dashboard.html', context)


@admin_required
def pending_products(request):
    """
    View all pending products waiting for admin approval
    """
    products = Product.objects.filter(is_approved=False, is_rejected=False).select_related('seller').order_by('-id')
    
    context = {
        'products': products,
        'page_title': 'Pending Products',
    }
    return render(request, 'admin_panel/pending_products.html', context)


@admin_required
def approved_products(request):
    """
    View all approved products
    """
    products = Product.objects.filter(is_approved=True).select_related('seller').order_by('-id')
    
    context = {
        'products': products,
        'page_title': 'Approved Products',
    }
    return render(request, 'admin_panel/approved_products.html', context)


@admin_required
@require_http_methods(["POST"])
def approve_product(request, product_id):
    """
    Approve a pending product
    """
    product = get_object_or_404(Product, id=product_id)
    product.is_approved = True
    product.save()
    
    messages.success(request, f"Product '{product.name}' has been approved.")
    return redirect('pending_products')


@admin_required
@require_http_methods(["POST"])
def reject_product(request, product_id):
    """
    Reject a pending product
    """
    product = get_object_or_404(Product, id=product_id)
    reason = request.POST.get('rejection_reason', '').strip()
    
    product.is_approved = False
    product.is_rejected = True
    product.rejection_reason = reason
    product.save()
    
    messages.success(request, f"Product '{product.name}' has been rejected.")
    return redirect('pending_products')


@admin_required
@require_http_methods(["POST"])
def revoke_product(request, product_id):
    """
    Revoke an approved product (remove it from buyers' view)
    """
    product = get_object_or_404(Product, id=product_id)
    product.is_approved = False
    product.save()
    
    messages.warning(request, f"Product '{product.name}' has been revoked and is no longer available.")
    return redirect('approved_products')


@admin_required
def manage_sellers(request):
    """
    View and manage all sellers
    """
    sellers = User.objects.filter(role='seller', is_approved=True).select_related('seller_profile').order_by('-id')
    
    context = {
        'sellers': sellers,
        'page_title': 'Manage Sellers',
    }
    return render(request, 'admin_panel/manage_sellers.html', context)


@admin_required
def manage_buyers(request):
    """
    View and manage all buyers
    """
    buyers = User.objects.filter(role='buyer', is_approved=True).select_related('buyer_profile').order_by('-id')
    
    context = {
        'buyers': buyers,
        'page_title': 'Manage Buyers',
    }
    return render(request, 'admin_panel/manage_buyers.html', context)


@admin_required
@require_http_methods(["POST"])
def ban_user(request, user_id):
    """
    Ban/deactivate a user (buyer or seller)
    """
    user = get_object_or_404(User, id=user_id, role__in=['buyer', 'seller'])
    user.is_active = False
    user.save()
    
    user_type = 'Seller' if user.role == 'seller' else 'Buyer'
    messages.warning(request, f"{user_type} '{user.username}' has been banned.")
    
    # Redirect back to appropriate list
    next_page = request.POST.get('next', 'manage_sellers' if user.role == 'seller' else 'manage_buyers')
    return redirect(next_page)


@admin_required
@require_http_methods(["POST"])
def unban_user(request, user_id):
    """
    Unban/reactivate a user (buyer or seller)
    """
    user = get_object_or_404(User, id=user_id, role__in=['buyer', 'seller'])
    user.is_active = True
    user.save()
    
    user_type = 'Seller' if user.role == 'seller' else 'Buyer'
    messages.success(request, f"{user_type} '{user.username}' has been unbanned.")
    
    next_page = request.POST.get('next', 'manage_sellers' if user.role == 'seller' else 'manage_buyers')
    return redirect(next_page)


@admin_required
def pending_users(request):
    """
    View all pending users waiting for admin approval
    """
    pending_users = User.objects.filter(is_approved=False, role__in=['buyer', 'seller']).order_by('-id')
    
    context = {
        'pending_users': pending_users,
        'page_title': 'Pending Users',
    }
    return render(request, 'admin_panel/pending_users.html', context)


@admin_required
@require_http_methods(["POST"])
def approve_user(request, user_id):
    """
    Approve a pending user
    """
    user = get_object_or_404(User, id=user_id, role__in=['buyer', 'seller'])
    user.is_approved = True
    user.save()
    
    user_type = 'Seller' if user.role == 'seller' else 'Buyer'
    messages.success(request, f"{user_type} '{user.username}' has been approved.")
    return redirect('pending_users')


@admin_required
@require_http_methods(["POST"])
def reject_user(request, user_id):
    """
    Reject and delete a pending user
    """
    user = get_object_or_404(User, id=user_id, role__in=['buyer', 'seller'])
    username = user.username
    user_type = 'Seller' if user.role == 'seller' else 'Buyer'
    user.delete()
    
    messages.success(request, f"{user_type} '{username}' has been rejected and deleted.")
    return redirect('pending_users')

