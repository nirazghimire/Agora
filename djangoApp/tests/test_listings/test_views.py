"""Tests for listings.views — create_listing."""
from decimal import Decimal

from django.test import TestCase, Client
from django.urls import reverse
from users.models import User, Address
from listings.models import Product, Review
from orders.models import Order, OrderItem


class CreateListingViewTests(TestCase):
    """Tests for the create_listing view."""

    def setUp(self):
        self.client = Client()
        self.seller = User.objects.create_user(
            username="lstseller", password="testpass123", role="seller"
        )
        self.buyer = User.objects.create_user(
            username="lstbuyer", password="testpass123", role="buyer"
        )
        self.url = reverse("create_listing")

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response.url)

    def test_buyer_redirected_to_home(self):
        self.client.login(username="lstbuyer", password="testpass123")
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse("home"))

    def test_seller_can_access_form(self):
        self.client.login(username="lstseller", password="testpass123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.context)

    def test_seller_cannot_access_as_buyer(self):
        self.client.login(username="lstbuyer", password="testpass123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)


class ProductDetailViewTests(TestCase):
    """Tests for product detail visibility and review rendering."""

    def setUp(self):
        self.client = Client()
        self.seller = User.objects.create_user(
            username="detail_seller", password="testpass123", role="seller"
        )
        self.buyer = User.objects.create_user(
            username="detail_buyer", password="testpass123", role="buyer"
        )
        self.product = Product.objects.create(
            seller=self.seller,
            is_approved=True,
            name="Detail Product",
            price=Decimal("99.99"),
            image="products/detail.jpg",
            stock_quantity=10,
            category="Electronics",
            color="Black",
            model_number=1001,
            brand="Acme",
            description="A detailed product",
        )

    def test_approved_product_detail_shows_empty_review_state(self):
        response = self.client.get(reverse("product_detail", args=[self.product.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Detail Product")
        self.assertContains(response, "No reviews so far for this product.")

    def test_product_detail_shows_product_specific_reviews(self):
        Review.objects.create(
            product=self.product,
            buyer=self.buyer,
            rating=5,
            comment="Excellent product",
        )
        response = self.client.get(reverse("product_detail", args=[self.product.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Excellent product")
        self.assertContains(response, "detail_buyer")

    def test_unapproved_product_hidden_from_non_owner(self):
        self.product.is_approved = False
        self.product.save(update_fields=["is_approved"])
        response = self.client.get(reverse("product_detail", args=[self.product.id]))
        self.assertEqual(response.status_code, 404)

    def test_unapproved_product_visible_to_owner(self):
        self.product.is_approved = False
        self.product.save(update_fields=["is_approved"])
        self.client.login(username="detail_seller", password="testpass123")
        response = self.client.get(reverse("product_detail", args=[self.product.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Detail Product")


class SubmitReviewViewTests(TestCase):
    """Tests for submitting reviews through purchase history flow."""

    def setUp(self):
        self.client = Client()
        self.seller = User.objects.create_user(
            username="review_seller", password="testpass123", role="seller"
        )
        self.buyer = User.objects.create_user(
            username="review_buyer", password="testpass123", role="buyer"
        )
        self.other_buyer = User.objects.create_user(
            username="review_other", password="testpass123", role="buyer"
        )
        self.product = Product.objects.create(
            seller=self.seller,
            is_approved=True,
            name="Review Product",
            price=Decimal("40.00"),
            image="products/review.jpg",
            stock_quantity=10,
            category="Books",
            color="Blue",
            model_number=2002,
            brand="Agora",
            description="Review flow product",
        )
        self.address = Address.objects.create(
            user=self.buyer,
            country="United States",
            state="CA",
            street="100 Main St",
            zip_code=90001,
        )
        self.order = Order.objects.create(
            buyer=self.buyer,
            shipping_address=self.address,
            country="United States",
            state="CA",
            street="100 Main St",
            zip_code=90001,
            subtotal=Decimal("40.00"),
            tax=Decimal("2.80"),
            shipping_fee=Decimal("10.00"),
            total=Decimal("52.80"),
        )
        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            seller=self.seller,
            product_name=self.product.name,
            unit_price=self.product.price,
            quantity=1,
        )

    def test_buyer_can_submit_review_for_purchased_product(self):
        self.client.login(username="review_buyer", password="testpass123")
        response = self.client.post(
            reverse("submit_review", args=[self.product.id]),
            {"rating": "5", "comment": "Worth every penny"},
        )
        self.assertRedirects(response, reverse("purchase_history"))
        self.assertTrue(
            Review.objects.filter(
                product=self.product,
                buyer=self.buyer,
                rating=5,
                comment="Worth every penny",
            ).exists()
        )

    def test_buyer_cannot_submit_review_without_purchase(self):
        self.client.login(username="review_other", password="testpass123")
        response = self.client.post(
            reverse("submit_review", args=[self.product.id]),
            {"rating": "4", "comment": "Nice"},
        )
        self.assertRedirects(response, reverse("purchase_history"))
        self.assertFalse(
            Review.objects.filter(product=self.product, buyer=self.other_buyer).exists()
        )
