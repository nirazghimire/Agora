from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from listings.models import Product

User = get_user_model()

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)

    def get_total_price(self):
        return sum(item.get_cost() for item in self.items.all())

    def __str__(self):
        return f"Cart for {self.user.username}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def get_cost(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.quantity} of {self.product.name}"


class Order(models.Model):
    STATUS_PLACED = 'placed'
    STATUS_SHIPPED = 'shipped'
    STATUS_DELIVERED = 'delivered'
    STATUS_CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (STATUS_PLACED, 'Placed'),
        (STATUS_SHIPPED, 'Shipped'),
        (STATUS_DELIVERED, 'Delivered'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchased_orders')
    shipping_address = models.ForeignKey(
        'users.Address',
        on_delete=models.SET_NULL,
        related_name='orders',
        null=True,
        blank=True,
    )
    country = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    street = models.CharField(max_length=255)
    zip_code = models.IntegerField()

    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PLACED)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.id} by {self.buyer.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='order_items')
    seller = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sold_order_items')

    product_name = models.CharField(max_length=255)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.quantity} x {self.product_name} (Order #{self.order_id})"

    @property
    def line_total(self):
        return self.unit_price * self.quantity

    def initiate_return(self, buyer, reason):
        if buyer != self.order.buyer:
            raise ValidationError('Only the buyer who placed the order can initiate a return.')

        if hasattr(self, 'return_request'):
            raise ValidationError('A return request has already been initiated for this item.')

        clean_reason = (reason or '').strip()
        if not clean_reason:
            raise ValidationError('Return reason is required.')

        return ReturnRequest.objects.create(
            order_item=self,
            buyer=buyer,
            seller=self.seller,
            reason=clean_reason,
        )


class ReturnRequest(models.Model):
    STATUS_REQUESTED = 'requested'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    STATUS_RECEIVED = 'received'
    STATUS_REFUNDED = 'refunded'

    STATUS_CHOICES = [
        (STATUS_REQUESTED, 'Requested'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
        (STATUS_RECEIVED, 'Received'),
        (STATUS_REFUNDED, 'Refunded'),
    ]

    order_item = models.OneToOneField(OrderItem, on_delete=models.CASCADE, related_name='return_request')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='return_requests')
    seller = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='received_return_requests')
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_REQUESTED)
    requested_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-requested_at']

    def clean(self):
        if self.buyer_id and self.order_item_id and self.buyer_id != self.order_item.order.buyer_id:
            raise ValidationError('Buyer must match the order buyer for this return request.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Return for {self.order_item.product_name} (Order #{self.order_item.order_id})"
