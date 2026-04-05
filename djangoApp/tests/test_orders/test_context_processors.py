"""Tests for orders.context_processors — cart_item_count."""
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser
from decimal import Decimal
from users.models import User
from listings.models import Product
from orders.models import Cart, CartItem
from orders.context_processors import cart_item_count


class CartItemCountContextProcessorTests(TestCase):
    """Tests for the cart_item_count context processor."""

    def setUp(self):
        self.factory = RequestFactory()
        self.seller_user = User.objects.create_user(
            username="cpseller", password="testpass123", role="seller"
        )
        self.buyer_user = User.objects.create_user(
            username="cpbuyer", password="testpass123", role="buyer"
        )
        self.product = Product.objects.create(
            seller=self.seller_user, name="CPProd", price=Decimal("10.00"),
            stock_quantity=5, category="C", color="R",
            model_number=1, brand="B", description="D",
            image="products/t.jpg",
        )

    def test_anonymous_user_returns_zero(self):
        request = self.factory.get("/")
        request.user = AnonymousUser()
        result = cart_item_count(request)
        self.assertEqual(result["cart_item_count"], 0)

    def test_seller_returns_zero(self):
        request = self.factory.get("/")
        request.user = self.seller_user
        result = cart_item_count(request)
        self.assertEqual(result["cart_item_count"], 0)

    def test_buyer_with_empty_cart_returns_zero(self):
        request = self.factory.get("/")
        request.user = self.buyer_user
        result = cart_item_count(request)
        self.assertEqual(result["cart_item_count"], 0)

    def test_buyer_with_items_returns_total_quantity(self):
        cart = Cart.objects.create(user=self.buyer_user)
        CartItem.objects.create(cart=cart, product=self.product, quantity=3)
        p2 = Product.objects.create(
            seller=self.seller_user, name="P2", price=Decimal("5.00"),
            stock_quantity=5, category="C", color="R",
            model_number=2, brand="B", description="D",
            image="products/t.jpg",
        )
        CartItem.objects.create(cart=cart, product=p2, quantity=2)

        request = self.factory.get("/")
        request.user = self.buyer_user
        result = cart_item_count(request)
        self.assertEqual(result["cart_item_count"], 5)
