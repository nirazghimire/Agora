from django.db.models import Sum

from .models import CartItem


def cart_item_count(request):
    if not request.user.is_authenticated or getattr(request.user, 'is_seller', False):
        return {'cart_item_count': 0}

    count = (
        CartItem.objects.filter(cart__user=request.user)
        .aggregate(total_quantity=Sum('quantity'))
        .get('total_quantity')
        or 0
    )
    return {'cart_item_count': int(count)}
