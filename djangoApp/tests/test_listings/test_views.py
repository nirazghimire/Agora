"""Tests for listings.views — create_listing."""
from django.test import TestCase, Client
from django.urls import reverse
from users.models import User
from listings.models import Product


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
