"""Tests for users.forms — ProfileEditForm."""
from django.test import TestCase
from users.forms import ProfileEditForm
from users.models import User


class ProfileEditFormTests(TestCase):
    """Tests for the ProfileEditForm."""

    def test_form_fields(self):
        form = ProfileEditForm()
        self.assertEqual(
            list(form.fields.keys()),
            ["first_name", "last_name", "email", "bio"],
        )

    def test_valid_data(self):
        user = User.objects.create_user(
            username="formuser", password="testpass123", role="buyer"
        )
        form = ProfileEditForm(
            data={
                "first_name": "Alice",
                "last_name": "Smith",
                "email": "alice@example.com",
                "bio": "Hello world",
            },
            instance=user,
        )
        self.assertTrue(form.is_valid())

    def test_blank_fields_allowed(self):
        """first_name, last_name, bio are not required by default on AbstractUser."""
        user = User.objects.create_user(
            username="blankuser", password="testpass123", role="buyer"
        )
        form = ProfileEditForm(
            data={
                "first_name": "",
                "last_name": "",
                "email": "blank@example.com",
                "bio": "",
            },
            instance=user,
        )
        self.assertTrue(form.is_valid())

    def test_widgets_have_css_class(self):
        form = ProfileEditForm()
        for field_name in form.fields:
            widget_attrs = form.fields[field_name].widget.attrs
            self.assertEqual(widget_attrs.get("class"), "form-input")
