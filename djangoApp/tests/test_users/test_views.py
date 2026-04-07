"""Tests for users.views — profile_view, profile_edit."""
from django.test import TestCase, Client
from django.urls import reverse
from users.models import User


class ProfileViewTests(TestCase):
    """Tests for the profile_view."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="viewuser", password="testpass123", role="buyer"
        )
        self.url = reverse("profile")

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response.url)

    def test_accessible_when_logged_in(self):
        self.client.login(username="viewuser", password="testpass123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_context_contains_profile_user(self):
        self.client.login(username="viewuser", password="testpass123")
        response = self.client.get(self.url)
        self.assertEqual(response.context["profile_user"], self.user)


class ProfileEditViewTests(TestCase):
    """Tests for the profile_edit view."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="edituser",
            password="testpass123",
            role="seller",
            email="old@example.com",
        )
        self.url = reverse("profile_edit")

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_get_returns_form(self):
        self.client.login(username="edituser", password="testpass123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.context)

    def test_post_valid_data_updates_profile(self):
        self.client.login(username="edituser", password="testpass123")
        response = self.client.post(
            self.url,
            {
                "first_name": "New",
                "last_name": "Name",
                "email": "new@example.com",
                "bio": "Updated bio",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "New")
        self.assertEqual(self.user.email, "new@example.com")
        self.assertEqual(self.user.bio, "Updated bio")

    def test_post_redirects_to_profile(self):
        self.client.login(username="edituser", password="testpass123")
        response = self.client.post(
            self.url,
            {
                "first_name": "X",
                "last_name": "Y",
                "email": "xy@example.com",
                "bio": "",
            },
        )
        self.assertRedirects(response, reverse("profile"))
