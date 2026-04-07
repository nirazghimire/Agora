"""Tests for orders.models — Cart, CartItem."""
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.test import TestCase
from users.models import User
from users.models import Address
from listings.models import Product
from orders.models import Cart, CartItem, Order, OrderItem, ReturnRequest


class CartModelTests(TestCase):
    """Tests for the Cart model."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="cartuser", password="testpass123", role="buyer"
        )
        self.cart = Cart.objects.create(user=self.user)
        self.seller = User.objects.create_user(
            username="cartseller", password="testpass123", role="seller"
        )

    def test_str_representation(self):
        self.assertEqual(str(self.cart), "Cart for cartuser")

    def test_get_total_price_empty_cart(self):
        self.assertEqual(self.cart.get_total_price(), 0)

    def test_get_total_price_with_items(self):
        p1 = Product.objects.create(
            seller=self.seller, name="A", price=Decimal("10.00"),
            stock_quantity=5, category="C", color="R",
            model_number=1, brand="B", description="D",
            image="products/t.jpg",
        )
        p2 = Product.objects.create(
            seller=self.seller, name="B", price=Decimal("20.00"),
            stock_quantity=5, category="C", color="R",
            model_number=2, brand="B", description="D",
            image="products/t.jpg",
        )
        CartItem.objects.create(cart=self.cart, product=p1, quantity=2)
        CartItem.objects.create(cart=self.cart, product=p2, quantity=1)
        # 10*2 + 20*1 = 40
        self.assertEqual(self.cart.get_total_price(), Decimal("40.00"))

    def test_one_cart_per_user(self):
        with self.assertRaises(Exception):
            Cart.objects.create(user=self.user)


class CartItemModelTests(TestCase):
    """Tests for the CartItem model."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="ciuser", password="testpass123", role="buyer"
        )
        self.seller = User.objects.create_user(
            username="ciseller", password="testpass123", role="seller"
        )
        self.cart = Cart.objects.create(user=self.user)
        self.product = Product.objects.create(
            seller=self.seller, name="Item", price=Decimal("15.50"),
            stock_quantity=10, category="C", color="B",
            model_number=1, brand="X", description="D",
            image="products/t.jpg",
        )

    def test_get_cost(self):
        item = CartItem.objects.create(
            cart=self.cart, product=self.product, quantity=3
        )
        self.assertEqual(item.get_cost(), Decimal("46.50"))

    def test_str_representation(self):
        item = CartItem.objects.create(
            cart=self.cart, product=self.product, quantity=2
        )
        self.assertEqual(str(item), "2 of Item")

    def test_default_quantity_is_one(self):
        item = CartItem.objects.create(cart=self.cart, product=self.product)
        self.assertEqual(item.quantity, 1)


class OrderAndReturnModelTests(TestCase):
    """Tests for Order, OrderItem, and ReturnRequest models."""

    def setUp(self):
        self.buyer = User.objects.create_user(
            username="orderbuyer", password="testpass123", role="buyer"
        )
        self.seller = User.objects.create_user(
            username="orderseller", password="testpass123", role="seller"
        )
        self.other_buyer = User.objects.create_user(
            username="otherbuyer", password="testpass123", role="buyer"
        )
        self.address = Address.objects.create(
            user=self.buyer,
            country="United States",
            state="CA",
            street="101 Main",
            zip_code=90001,
        )
        self.product = Product.objects.create(
            seller=self.seller,
            name="History Product",
            price=Decimal("35.00"),
            stock_quantity=10,
            category="C",
            color="B",
            model_number=7,
            brand="X",
            description="D",
            image="products/t.jpg",
        )
        self.order = Order.objects.create(
            buyer=self.buyer,
            shipping_address=self.address,
            country="United States",
            state="CA",
            street="101 Main",
            zip_code=90001,
            subtotal=Decimal("35.00"),
            tax=Decimal("2.45"),
            shipping_fee=Decimal("10.00"),
            total=Decimal("47.45"),
        )
        self.order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            seller=self.seller,
            product_name=self.product.name,
            unit_price=self.product.price,
            quantity=2,
        )

    def test_order_str_representation(self):
        self.assertEqual(str(self.order), f"Order #{self.order.id} by orderbuyer")

    def test_order_item_line_total(self):
        self.assertEqual(self.order_item.line_total, Decimal("70.00"))

    def test_buyer_can_initiate_return(self):
        request = self.order_item.initiate_return(self.buyer, "Wrong size")
        self.assertEqual(request.status, ReturnRequest.STATUS_REQUESTED)
        self.assertEqual(request.buyer, self.buyer)
        self.assertEqual(request.seller, self.seller)

    def test_other_user_cannot_initiate_return(self):
        with self.assertRaises(ValidationError):
            self.order_item.initiate_return(self.other_buyer, "Not mine")

    def test_duplicate_return_is_not_allowed(self):
        self.order_item.initiate_return(self.buyer, "First request")
        with self.assertRaises(ValidationError):
            self.order_item.initiate_return(self.buyer, "Second request")
