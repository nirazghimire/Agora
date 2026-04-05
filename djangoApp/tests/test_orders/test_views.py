"""Tests for orders.views — cart operations and checkout."""
from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from users.models import User, Address
from listings.models import Product
from orders.models import Cart, CartItem, Order, OrderItem, ReturnRequest


class CartDetailViewTests(TestCase):
    """Tests for cart_detail view."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="cduser", password="testpass123", role="buyer"
        )
        self.url = reverse("cart_detail")

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_accessible_when_logged_in(self):
        self.client.login(username="cduser", password="testpass123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_creates_cart_if_not_exists(self):
        self.client.login(username="cduser", password="testpass123")
        self.assertFalse(Cart.objects.filter(user=self.user).exists())
        self.client.get(self.url)
        self.assertTrue(Cart.objects.filter(user=self.user).exists())


class AddToCartViewTests(TestCase):
    """Tests for add_to_cart view."""

    def setUp(self):
        self.client = Client()
        self.buyer = User.objects.create_user(
            username="atcbuyer", password="testpass123", role="buyer"
        )
        self.seller = User.objects.create_user(
            username="atcseller", password="testpass123", role="seller"
        )
        self.product = Product.objects.create(
            seller=self.seller, name="CartProd", price=Decimal("20.00"),
            stock_quantity=10, category="C", color="R",
            model_number=1, brand="B", description="D",
            image="products/t.jpg", is_approved=True,
        )

    def test_anonymous_user_redirected(self):
        url = reverse("add_to_cart", args=[self.product.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

    def test_buyer_can_add_to_cart(self):
        self.client.login(username="atcbuyer", password="testpass123")
        url = reverse("add_to_cart", args=[self.product.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        cart = Cart.objects.get(user=self.buyer)
        self.assertEqual(cart.items.count(), 1)
        self.assertEqual(cart.items.first().quantity, 1)

    def test_adding_same_product_increments_quantity(self):
        self.client.login(username="atcbuyer", password="testpass123")
        url = reverse("add_to_cart", args=[self.product.id])
        self.client.post(url)
        self.client.post(url)
        cart = Cart.objects.get(user=self.buyer)
        self.assertEqual(cart.items.first().quantity, 2)

    def test_seller_redirected_to_home(self):
        self.client.login(username="atcseller", password="testpass123")
        url = reverse("add_to_cart", args=[self.product.id])
        response = self.client.post(url)
        self.assertRedirects(response, reverse("home"))

    def test_ajax_returns_json(self):
        self.client.login(username="atcbuyer", password="testpass123")
        url = reverse("add_to_cart", args=[self.product.id])
        response = self.client.post(
            url, HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["cart_count"], 1)

    def test_ajax_anonymous_returns_401(self):
        url = reverse("add_to_cart", args=[self.product.id])
        response = self.client.post(
            url, HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(response.status_code, 401)

    def test_get_not_allowed(self):
        self.client.login(username="atcbuyer", password="testpass123")
        url = reverse("add_to_cart", args=[self.product.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)


class RemoveFromCartViewTests(TestCase):
    """Tests for remove_from_cart view."""

    def setUp(self):
        self.client = Client()
        self.buyer = User.objects.create_user(
            username="rmbuyer", password="testpass123", role="buyer"
        )
        self.seller = User.objects.create_user(
            username="rmseller", password="testpass123", role="seller"
        )
        self.product = Product.objects.create(
            seller=self.seller, name="RmProd", price=10,
            stock_quantity=5, category="C", color="R",
            model_number=1, brand="B", description="D",
            image="products/t.jpg", is_approved=True,
        )
        self.client.login(username="rmbuyer", password="testpass123")
        self.cart = Cart.objects.create(user=self.buyer)
        CartItem.objects.create(cart=self.cart, product=self.product, quantity=2)

    def test_remove_item(self):
        url = reverse("remove_from_cart", args=[self.product.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.cart.items.count(), 0)


class IncrementDecrementCartItemTests(TestCase):
    """Tests for increment_cart_item and decrement_cart_item views."""

    def setUp(self):
        self.client = Client()
        self.buyer = User.objects.create_user(
            username="incbuyer", password="testpass123", role="buyer"
        )
        self.seller = User.objects.create_user(
            username="incseller", password="testpass123", role="seller"
        )
        self.product = Product.objects.create(
            seller=self.seller, name="IncProd", price=10,
            stock_quantity=5, category="C", color="R",
            model_number=1, brand="B", description="D",
            image="products/t.jpg", is_approved=True,
        )
        self.client.login(username="incbuyer", password="testpass123")
        self.cart = Cart.objects.create(user=self.buyer)
        self.item = CartItem.objects.create(
            cart=self.cart, product=self.product, quantity=2
        )

    def test_increment(self):
        url = reverse("increment_cart_item", args=[self.product.id])
        self.client.post(url)
        self.item.refresh_from_db()
        self.assertEqual(self.item.quantity, 3)

    def test_decrement(self):
        url = reverse("decrement_cart_item", args=[self.product.id])
        self.client.post(url)
        self.item.refresh_from_db()
        self.assertEqual(self.item.quantity, 1)

    def test_decrement_to_zero_removes_item(self):
        self.item.quantity = 1
        self.item.save()
        url = reverse("decrement_cart_item", args=[self.product.id])
        self.client.post(url)
        self.assertEqual(self.cart.items.count(), 0)


class CheckoutViewTests(TestCase):
    """Tests for the checkout view."""

    def setUp(self):
        self.client = Client()
        self.buyer = User.objects.create_user(
            username="cobuyer", password="testpass123", role="buyer"
        )
        self.seller = User.objects.create_user(
            username="coseller", password="testpass123", role="seller"
        )
        self.product = Product.objects.create(
            seller=self.seller, name="COProd", price=Decimal("50.00"),
            stock_quantity=5, category="C", color="R",
            model_number=1, brand="B", description="D",
            image="products/t.jpg", is_approved=True,
        )
        self.client.login(username="cobuyer", password="testpass123")
        self.cart = Cart.objects.create(user=self.buyer)
        CartItem.objects.create(cart=self.cart, product=self.product, quantity=1)
        self.url = reverse("checkout")

    def test_seller_redirected(self):
        self.client.logout()
        self.client.login(username="coseller", password="testpass123")
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse("home"))

    def test_empty_cart_redirects(self):
        self.cart.items.all().delete()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_get_checkout_page(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("totals", response.context)

    def test_checkout_with_new_address(self):
        response = self.client.post(self.url, {
            "state": "CA",
            "street": "456 Elm",
            "zip_code": "90001",
        })
        self.assertEqual(response.status_code, 302)
        # Cart should be emptied after checkout
        self.assertEqual(self.cart.items.count(), 0)
        # Address should be created
        self.assertTrue(
            Address.objects.filter(user=self.buyer, street="456 Elm").exists()
        )
        self.assertTrue(
            Address.objects.filter(user=self.buyer, street="456 Elm", country="United States").exists()
        )

        order = Order.objects.get(buyer=self.buyer)
        self.assertEqual(order.country, "United States")
        self.assertEqual(order.items.count(), 1)

        order_item = OrderItem.objects.get(order=order)
        self.assertEqual(order_item.seller, self.seller)
        self.assertEqual(order_item.product_name, "COProd")

    def test_checkout_with_existing_address(self):
        addr = Address.objects.create(
            user=self.buyer, country="USA", state="TX",
            street="789 Oak", zip_code=75001,
        )
        response = self.client.post(self.url, {
            "selected_address_id": str(addr.id),
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.cart.items.count(), 0)

    def test_checkout_missing_address_fields(self):
        response = self.client.post(self.url, {
            "country": "",
            "state": "",
            "street": "",
            "zip_code": "",
        })
        self.assertEqual(response.status_code, 200)
        # Cart should not be emptied
        self.assertEqual(self.cart.items.count(), 1)

    def test_checkout_invalid_zip_code(self):
        response = self.client.post(self.url, {
            "state": "CA",
            "street": "123 St",
            "zip_code": "abc",
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.cart.items.count(), 1)


class ReturnWorkflowViewTests(TestCase):
    """Tests for purchase/sales history and return interactions."""

    def setUp(self):
        self.client = Client()
        self.buyer = User.objects.create_user(
            username="rwbuyer", password="testpass123", role="buyer"
        )
        self.seller = User.objects.create_user(
            username="rwseller", password="testpass123", role="seller"
        )
        self.product = Product.objects.create(
            seller=self.seller,
            name="Returnable",
            price=Decimal("40.00"),
            stock_quantity=10,
            category="C",
            color="R",
            model_number=3,
            brand="B",
            description="D",
            image="products/t.jpg",
            is_approved=True,
        )
        self.address = Address.objects.create(
            user=self.buyer,
            country="United States",
            state="CA",
            street="A St",
            zip_code=90001,
        )
        self.order = Order.objects.create(
            buyer=self.buyer,
            shipping_address=self.address,
            country="United States",
            state="CA",
            street="A St",
            zip_code=90001,
            subtotal=Decimal("40.00"),
            tax=Decimal("2.80"),
            shipping_fee=Decimal("10.00"),
            total=Decimal("52.80"),
        )
        self.order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            seller=self.seller,
            product_name=self.product.name,
            unit_price=self.product.price,
            quantity=1,
        )

    def test_buyer_can_view_purchase_history(self):
        self.client.login(username="rwbuyer", password="testpass123")
        response = self.client.get(reverse("purchase_history"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Order #")

    def test_buyer_can_initiate_return(self):
        self.client.login(username="rwbuyer", password="testpass123")
        response = self.client.post(
            reverse("initiate_return", args=[self.order_item.id]),
            {"reason": "Item not as described"},
        )
        self.assertEqual(response.status_code, 302)
        rr = ReturnRequest.objects.get(order_item=self.order_item)
        self.assertEqual(rr.status, ReturnRequest.STATUS_REQUESTED)

    def test_seller_can_view_sales_history(self):
        self.client.login(username="rwseller", password="testpass123")
        response = self.client.get(reverse("sales_history"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sold Products")

    def test_seller_can_update_return_status(self):
        rr = self.order_item.initiate_return(self.buyer, "Defective")
        self.client.login(username="rwseller", password="testpass123")
        response = self.client.post(
            reverse("update_return_request", args=[rr.id]),
            {"status": ReturnRequest.STATUS_APPROVED},
        )
        self.assertEqual(response.status_code, 302)
        rr.refresh_from_db()
        self.assertEqual(rr.status, ReturnRequest.STATUS_APPROVED)
