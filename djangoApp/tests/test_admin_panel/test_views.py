"""Tests for admin_panel.views — dashboard, product & user management."""
from django.test import TestCase, Client
from django.urls import reverse
from users.models import User
from listings.models import Product


class AdminViewTestMixin:
    """Common setup for admin panel view tests."""

    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(
            username="apnadmin", password="testpass123", role="admin",
            is_staff=True,
        )
        self.seller = User.objects.create_user(
            username="apnseller", password="testpass123", role="seller"
        )
        self.buyer = User.objects.create_user(
            username="apnbuyer", password="testpass123", role="buyer"
        )
        self.client.login(username="apnadmin", password="testpass123")


class AdminDashboardTests(AdminViewTestMixin, TestCase):
    """Tests for admin_dashboard view."""

    def test_dashboard_accessible_by_admin(self):
        response = self.client.get(reverse("admin_dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_blocked_for_buyer(self):
        self.client.logout()
        self.client.login(username="apnbuyer", password="testpass123")
        response = self.client.get(reverse("admin_dashboard"))
        self.assertEqual(response.status_code, 403)

    def test_dashboard_stats_in_context(self):
        response = self.client.get(reverse("admin_dashboard"))
        stats = response.context["stats"]
        self.assertIn("total_users", stats)
        self.assertIn("total_sellers", stats)
        self.assertIn("total_buyers", stats)
        self.assertIn("pending_products", stats)


class ProductManagementTests(AdminViewTestMixin, TestCase):
    """Tests for approve, reject, revoke product views."""

    def setUp(self):
        super().setUp()
        self.product = Product.objects.create(
            seller=self.seller, name="Widget", price=25, stock_quantity=10,
            category="Electronics", color="Black", model_number=100,
            brand="Acme", description="A widget", image="products/w.jpg",
            is_approved=False,
        )

    def test_pending_products_page(self):
        response = self.client.get(reverse("pending_products"))
        self.assertEqual(response.status_code, 200)
        names = [p.name for p in response.context["products"]]
        self.assertIn("Widget", names)

    def test_approve_product(self):
        response = self.client.post(
            reverse("approve_product", args=[self.product.id])
        )
        self.assertEqual(response.status_code, 302)
        self.product.refresh_from_db()
        self.assertTrue(self.product.is_approved)

    def test_reject_product_marks_rejected(self):
        pid = self.product.id
        response = self.client.post(
            reverse("reject_product", args=[pid]),
            data={"rejection_reason": "Not appropriate"}
        )
        self.assertEqual(response.status_code, 302)
        self.product.refresh_from_db()
        self.assertTrue(self.product.is_rejected)
        self.assertEqual(self.product.rejection_reason, "Not appropriate")

    def test_revoke_approved_product(self):
        self.product.is_approved = True
        self.product.save()
        response = self.client.post(
            reverse("revoke_product", args=[self.product.id])
        )
        self.assertEqual(response.status_code, 302)
        self.product.refresh_from_db()
        self.assertFalse(self.product.is_approved)

    def test_approved_products_page(self):
        self.product.is_approved = True
        self.product.save()
        response = self.client.get(reverse("approved_products"))
        self.assertEqual(response.status_code, 200)
        names = [p.name for p in response.context["products"]]
        self.assertIn("Widget", names)

    def test_approve_requires_post(self):
        response = self.client.get(
            reverse("approve_product", args=[self.product.id])
        )
        self.assertEqual(response.status_code, 405)


class UserManagementTests(AdminViewTestMixin, TestCase):
    """Tests for ban/unban and manage sellers/buyers views."""

    def test_manage_sellers_page(self):
        response = self.client.get(reverse("manage_sellers"))
        self.assertEqual(response.status_code, 200)

    def test_manage_buyers_page(self):
        response = self.client.get(reverse("manage_buyers"))
        self.assertEqual(response.status_code, 200)

    def test_ban_seller(self):
        response = self.client.post(
            reverse("ban_seller", args=[self.seller.id])
        )
        self.assertEqual(response.status_code, 302)
        self.seller.refresh_from_db()
        self.assertFalse(self.seller.is_active)

    def test_unban_seller(self):
        self.seller.is_active = False
        self.seller.save()
        response = self.client.post(
            reverse("unban_seller", args=[self.seller.id])
        )
        self.assertEqual(response.status_code, 302)
        self.seller.refresh_from_db()
        self.assertTrue(self.seller.is_active)

    def test_ban_buyer(self):
        response = self.client.post(
            reverse("ban_buyer", args=[self.buyer.id])
        )
        self.assertEqual(response.status_code, 302)
        self.buyer.refresh_from_db()
        self.assertFalse(self.buyer.is_active)

    def test_cannot_ban_admin_user(self):
        response = self.client.post(
            reverse("ban_seller", args=[self.admin.id])
        )
        self.assertEqual(response.status_code, 404)
