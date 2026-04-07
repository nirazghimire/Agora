"""Tests for accounts.views — home, signup, login_jwt, logout_jwt."""
from django.test import TestCase, Client
from django.urls import reverse
from users.models import User, Address
from listings.models import Product
from unittest.mock import patch


class HomeViewTests(TestCase):
    """Tests for the home view."""

    def setUp(self):
        self.client = Client()

    def test_anonymous_user_sees_approved_products(self):
        seller = User.objects.create_user(
            username="hseller", password="testpass123", role="seller"
        )
        Product.objects.create(
            seller=seller, name="Visible", price=10, stock_quantity=5,
            category="A", color="Red", model_number=1, brand="B",
            description="d", image="products/test.jpg", is_approved=True,
        )
        Product.objects.create(
            seller=seller, name="Hidden", price=10, stock_quantity=5,
            category="A", color="Red", model_number=2, brand="B",
            description="d", image="products/test.jpg", is_approved=False,
        )
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        products = list(response.context["products"])
        names = [p.name for p in products]
        self.assertIn("Visible", names)
        self.assertNotIn("Hidden", names)

    def test_seller_sees_own_products(self):
        seller = User.objects.create_user(
            username="ownerseller", password="testpass123", role="seller"
        )
        Product.objects.create(
            seller=seller, name="Mine", price=10, stock_quantity=5,
            category="A", color="Red", model_number=1, brand="B",
            description="d", image="products/test.jpg", is_approved=False,
        )
        self.client.login(username="ownerseller", password="testpass123")
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["is_seller_view"])
        names = [p.name for p in response.context["products"]]
        self.assertIn("Mine", names)

    def test_admin_user_redirected_to_dashboard(self):
        admin = User.objects.create_user(
            username="homeadmin", password="testpass123", role="admin",
            is_staff=True,
        )
        self.client.login(username="homeadmin", password="testpass123")
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("admin-panel", response.url)


class SignupViewTests(TestCase):
    """Tests for the signup view."""

    def setUp(self):
        self.client = Client()
        self.url = reverse("sign_up")

    def test_get_signup_page(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_successful_buyer_signup(self):
        response = self.client.post(self.url, {
            "username": "newbuyer",
            "email": "buyer@example.com",
            "password": "securepass1",
            "role": "buyer",
            "bio": "",
            "country": "USA",
            "state": "TX",
            "street": "123 Main",
            "zip_code": "75001",
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="newbuyer").exists())
        self.assertTrue(Address.objects.filter(user__username="newbuyer").exists())

    def test_successful_seller_signup(self):
        response = self.client.post(self.url, {
            "username": "newseller",
            "email": "seller@example.com",
            "password": "securepass1",
            "role": "seller",
            "bio": "I sell stuff",
            "country": "",
            "state": "",
            "street": "",
            "zip_code": "",
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="newseller").exists())

    def test_missing_required_fields(self):
        response = self.client.post(self.url, {
            "username": "",
            "email": "",
            "password": "",
            "role": "buyer",
        })
        # Should stay on signup page (200 re-render)
        self.assertEqual(response.status_code, 200)

    def test_duplicate_username(self):
        User.objects.create_user(username="taken", password="testpass123", role="buyer")
        response = self.client.post(self.url, {
            "username": "taken",
            "email": "unique@example.com",
            "password": "pass123",
            "role": "buyer",
            "country": "USA",
            "state": "TX",
            "street": "St",
            "zip_code": "75001",
        })
        self.assertEqual(response.status_code, 200)

    def test_duplicate_email(self):
        User.objects.create_user(
            username="orig", password="testpass123", role="buyer", email="dup@x.com"
        )
        response = self.client.post(self.url, {
            "username": "newname",
            "email": "dup@x.com",
            "password": "pass123",
            "role": "buyer",
            "country": "USA",
            "state": "TX",
            "street": "St",
            "zip_code": "75001",
        })
        self.assertEqual(response.status_code, 200)

    def test_buyer_missing_address_fields(self):
        response = self.client.post(self.url, {
            "username": "badbuyer",
            "email": "bb@example.com",
            "password": "pass123",
            "role": "buyer",
            "bio": "",
            "country": "",
            "state": "",
            "street": "",
            "zip_code": "",
        })
        self.assertEqual(response.status_code, 200)

    def test_non_digit_zip_code(self):
        response = self.client.post(self.url, {
            "username": "zipuser",
            "email": "zip@example.com",
            "password": "pass123",
            "role": "buyer",
            "country": "USA",
            "state": "TX",
            "street": "St",
            "zip_code": "abcde",
        })
        self.assertEqual(response.status_code, 200)


class LoginJWTViewTests(TestCase):
    """Tests for the login_jwt view."""

    def setUp(self):
        self.client = Client()
        self.url = reverse("login")
        self.user = User.objects.create_user(
            username="loginuser", password="testpass123", role="buyer",
            is_approved=True,
        )

    def test_get_login_page(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_successful_login_redirects(self):
        response = self.client.post(self.url, {
            "username": "loginuser",
            "password": "testpass123",
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("home"))

    def test_invalid_credentials(self):
        response = self.client.post(self.url, {
            "username": "loginuser",
            "password": "wrong",
        })
        self.assertEqual(response.status_code, 200)

    def test_banned_user_cannot_login(self):
        self.user.is_active = False
        self.user.save()
        response = self.client.post(self.url, {
            "username": "loginuser",
            "password": "testpass123",
        })
        self.assertEqual(response.status_code, 200)

    def test_admin_login_redirects_to_dashboard(self):
        admin = User.objects.create_user(
            username="lgadmin", password="testpass123", role="admin",
            is_staff=True,
        )
        response = self.client.post(self.url, {
            "username": "lgadmin",
            "password": "testpass123",
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn("admin-panel", response.url)

    def test_session_stores_jwt_tokens(self):
        self.client.post(self.url, {
            "username": "loginuser",
            "password": "testpass123",
        })
        session = self.client.session
        self.assertIn("jwt_access", session)
        self.assertIn("jwt_refresh", session)
        self.assertEqual(session["jwt_username"], "loginuser")


class LogoutJWTViewTests(TestCase):
    """Tests for the logout_jwt view."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="logoutuser", password="testpass123", role="buyer",
            is_approved=True,
        )
        self.client.login(username="logoutuser", password="testpass123")
        self.url = reverse("logout")

    def test_logout_redirects_to_home(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("home"))

    def test_get_not_allowed(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

    def test_session_cleared_after_logout(self):
        # First login to set session keys
        self.client.post(reverse("login"), {
            "username": "logoutuser",
            "password": "testpass123",
        })
        self.client.post(self.url)
        session = self.client.session
        self.assertNotIn("jwt_access", session)
        self.assertNotIn("jwt_refresh", session)
