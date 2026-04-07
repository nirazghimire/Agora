"""Tests for admin_panel.decorators — admin_required."""
from django.test import TestCase, Client, RequestFactory
from django.http import HttpResponse
from django.urls import reverse
from users.models import User
from admin_panel.decorators import admin_required


@admin_required
def _dummy_view(request):
    return HttpResponse("OK")


class AdminRequiredDecoratorTests(TestCase):
    """Tests for the admin_required decorator."""

    def setUp(self):
        self.factory = RequestFactory()
        self.buyer = User.objects.create_user(
            username="decbuyer", password="testpass123", role="buyer"
        )
        self.admin = User.objects.create_user(
            username="decadmin", password="testpass123", role="admin",
            is_staff=True,
        )

    def test_anonymous_redirected_to_login(self):
        from django.contrib.auth.models import AnonymousUser
        request = self.factory.get("/fake/")
        request.user = AnonymousUser()
        response = _dummy_view(request)
        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response.url)

    def test_non_staff_gets_403(self):
        request = self.factory.get("/fake/")
        request.user = self.buyer
        response = _dummy_view(request)
        self.assertEqual(response.status_code, 403)

    def test_staff_user_allowed(self):
        request = self.factory.get("/fake/")
        request.user = self.admin
        response = _dummy_view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"OK")
