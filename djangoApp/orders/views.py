from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.urls import reverse
from django.db import transaction
from django.core.exceptions import ValidationError
from listings.models import Product
from .models import Cart, CartItem, Order, OrderItem, ReturnRequest
from users.models import Address
from decimal import Decimal


TAX_RATE = Decimal("0.07")
SHIPPING_FEE = Decimal("10.00")
CHECKOUT_COUNTRY = "United States"

@login_required
def cart_detail(request):
    
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'orders/cart.html', {'cart': cart})


def _cart_item_count(cart):
    return sum(item.quantity for item in cart.items.all())


def _checkout_totals(cart):
    subtotal = cart.get_total_price()
    tax = round(subtotal * TAX_RATE, 2)
    shipping = 0 if subtotal == 0 else SHIPPING_FEE
    total = round(subtotal + tax + shipping, 2)
    return {
        'subtotal': subtotal,
        'tax': tax,
        'shipping': shipping,
        'total': total,
    }


def _create_order_from_cart(cart, buyer, selected_address, totals):
    order = Order.objects.create(
        buyer=buyer,
        shipping_address=selected_address,
        country=selected_address.country,
        state=selected_address.state,
        street=selected_address.street,
        zip_code=selected_address.zip_code,
        subtotal=totals['subtotal'],
        tax=totals['tax'],
        shipping_fee=totals['shipping'],
        total=totals['total'],
    )

    order_items = []
    for item in cart.items.select_related('product', 'product__seller'):
        if item.quantity > item.product.stock_quantity:
            raise ValidationError(f"Not enough stock for {item.product.name}. Available: {item.product.stock_quantity}.")
        
        item.product.stock_quantity -= item.quantity
        item.product.save(update_fields=['stock_quantity'])
        
        order_items.append(
            OrderItem(
                order=order,
                product=item.product,
                seller=item.product.seller,
                product_name=item.product.name,
                unit_price=item.product.price,
                quantity=item.quantity,
            )
        )
    OrderItem.objects.bulk_create(order_items)
    return order


@login_required
def checkout(request):
    if request.user.is_seller:
        return redirect('home')

    cart, created = Cart.objects.get_or_create(user=request.user)
    if not cart.items.exists():
        messages.warning(request, 'Your cart is empty.')
        return redirect('cart_detail')

    addresses = request.user.addresses.order_by('-updated_at', '-created_at')
    totals = _checkout_totals(cart)

    if request.method == 'POST':
        selected_address_id = request.POST.get('selected_address_id', '').strip()
        selected_address = None

        if selected_address_id:
            selected_address = addresses.filter(id=selected_address_id).first()

        if selected_address is None:
            country = CHECKOUT_COUNTRY
            state = request.POST.get('state', '').strip()
            street = request.POST.get('street', '').strip()
            zip_code = request.POST.get('zip_code', '').strip()

            if not country or not state or not street or not zip_code:
                messages.error(request, 'Please select an address or enter all address fields.')
                return render(
                    request,
                    'orders/checkout.html',
                    {
                        'cart': cart,
                        'addresses': addresses,
                        'totals': totals,
                        'selected_address_id': selected_address_id,
                    },
                )

            if not zip_code.isdigit():
                messages.error(request, 'Zip code must contain digits only.')
                return render(
                    request,
                    'orders/checkout.html',
                    {
                        'cart': cart,
                        'addresses': addresses,
                        'totals': totals,
                        'selected_address_id': selected_address_id,
                    },
                )

            selected_address = Address.objects.create(
                user=request.user,
                country=country,
                state=state,
                street=street,
                zip_code=int(zip_code),
            )

        try:
            with transaction.atomic():
                _create_order_from_cart(cart, request.user, selected_address, totals)
                cart.items.all().delete()
        except ValidationError as e:
            messages.error(request, e.message)
            return redirect('cart_detail')

        messages.success(
            request,
            f"Order placed successfully. Shipping to {selected_address.street}, {selected_address.state}.",
        )
        return redirect('home')

    return render(
        request,
        'orders/checkout.html',
        {
            'cart': cart,
            'addresses': addresses,
            'totals': totals,
        },
    )

@require_POST
def add_to_cart(request, product_id):
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'

    if not request.user.is_authenticated:
        login_message = 'You have to be logged in to start shopping.'
        messages.warning(request, login_message)
        if is_ajax:
            return JsonResponse(
                {
                    'success': False,
                    'redirect_url': reverse('login'),
                    'message': login_message,
                },
                status=401,
            )
        return redirect('login')

    if request.user.is_seller:
        return redirect('home')
        
    cart, created = Cart.objects.get_or_create(user=request.user)
    product = get_object_or_404(Product, id=product_id)
    
    try:
        cart_item = CartItem.objects.get(cart=cart, product=product)
        desired_quantity = cart_item.quantity + 1
    except CartItem.DoesNotExist:
        cart_item = None
        desired_quantity = 1

    if desired_quantity > product.stock_quantity:
        warning_msg = f"Sorry, only {product.stock_quantity} available in stock for {product.name}."
        if is_ajax:
            return JsonResponse({'success': False, 'message': warning_msg}, status=400)
        messages.warning(request, warning_msg)
        return redirect(request.META.get('HTTP_REFERER', 'home'))

    if cart_item:
        cart_item.quantity = desired_quantity
        cart_item.save()
    else:
        CartItem.objects.create(cart=cart, product=product, quantity=1)

    if is_ajax:
        return JsonResponse({'success': True, 'cart_count': _cart_item_count(cart)})
        
    messages.success(request, f"Added {product.name} to cart.")
    return redirect(request.META.get('HTTP_REFERER', 'home'))

@login_required
def remove_from_cart(request, product_id):
    if request.user.is_seller:
        return redirect('home')
        
    cart, created = Cart.objects.get_or_create(user=request.user)
    product = get_object_or_404(Product, id=product_id)
    CartItem.objects.filter(cart=cart, product=product).delete()
    
    return redirect('cart_detail')


@login_required
@require_POST
def increment_cart_item(request, product_id):
    if request.user.is_seller:
        return redirect('home')

    cart, created = Cart.objects.get_or_create(user=request.user)
    product = get_object_or_404(Product, id=product_id)
    cart_item = get_object_or_404(CartItem, cart=cart, product=product)
    
    if cart_item.quantity < product.stock_quantity:
        cart_item.quantity += 1
        cart_item.save()
    else:
        messages.warning(request, f"Sorry, only {product.stock_quantity} available in stock for {product.name}.")

    return redirect('cart_detail')


@login_required
@require_POST
def decrement_cart_item(request, product_id):
    if request.user.is_seller:
        return redirect('home')

    cart, created = Cart.objects.get_or_create(user=request.user)
    product = get_object_or_404(Product, id=product_id)
    cart_item = get_object_or_404(CartItem, cart=cart, product=product)

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()

    return redirect('cart_detail')


@login_required
def purchase_history(request):
    if request.user.is_seller:
        return redirect('home')

    orders = (
        Order.objects.filter(buyer=request.user)
        .prefetch_related('items__return_request')
        .order_by('-created_at')
    )
    return render(request, 'orders/purchase_history.html', {'orders': orders})


@login_required
@require_POST
def initiate_return(request, order_item_id):
    if request.user.is_seller:
        return redirect('home')

    order_item = get_object_or_404(
        OrderItem.objects.select_related('order', 'seller'),
        id=order_item_id,
        order__buyer=request.user,
    )
    reason = request.POST.get('reason', '')

    try:
        order_item.initiate_return(request.user, reason)
    except ValidationError as exc:
        messages.error(request, exc.messages[0])
    else:
        messages.success(request, 'Return request submitted successfully.')

    return redirect('purchase_history')


@login_required
def sales_history(request):
    if not request.user.is_seller:
        return redirect('home')

    sold_items = (
        OrderItem.objects.filter(seller=request.user)
        .select_related('order', 'order__buyer', 'return_request')
        .order_by('-created_at')
    )
    return render(request, 'orders/sales_history.html', {'sold_items': sold_items})


@login_required
@require_POST
def update_return_request(request, return_request_id):
    if not request.user.is_seller:
        return redirect('home')

    return_request = get_object_or_404(
        ReturnRequest,
        id=return_request_id,
        seller=request.user,
    )
    allowed_statuses = {
        ReturnRequest.STATUS_APPROVED,
        ReturnRequest.STATUS_REJECTED,
        ReturnRequest.STATUS_RECEIVED,
        ReturnRequest.STATUS_REFUNDED,
    }
    status = request.POST.get('status', '').strip()

    if status not in allowed_statuses:
        messages.error(request, 'Invalid return status selected.')
        return redirect('sales_history')

    return_request.status = status
    return_request.save(update_fields=['status', 'updated_at'])
    messages.success(request, 'Return request updated successfully.')
    return redirect('sales_history')
