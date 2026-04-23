from django.contrib.syndication.views import Feed
from django.urls import reverse
from .models import OrderItem
from django.utils.feedgenerator import Rss201rev2Feed

class LatestSellerSalesFeed(Feed):
    title = "My Recent Sales on Agora"
    link = "/seller/rss/sales/"
    description = "Updates on the latest sales of your products."
    feed_type = Rss201rev2Feed

    def get_object(self, request, *args, **kwargs):
        # Ensure only sellers can access this feed
        if not request.user.is_authenticated or not getattr(request.user, 'is_seller', False):
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("Only sellers can access this feed.")
        return request.user

    def items(self, obj):
        return OrderItem.objects.filter(seller=obj).order_by('-created_at')[:20]

    def item_title(self, item):
        return f"Sale: {item.quantity} x {item.product_name}"

    def item_description(self, item):
        return f"Order #{item.order.id} | Unit Price: ${item.unit_price} | Total: ${item.line_total}"

    def item_link(self, item):
        return reverse('sales_history')
