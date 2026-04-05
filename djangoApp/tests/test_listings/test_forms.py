"""Tests for listings.forms — ProductForm."""
from django.test import TestCase
from listings.forms import ProductForm


class ProductFormTests(TestCase):
    """Tests for the ProductForm."""

    def test_form_has_correct_fields(self):
        form = ProductForm()
        expected = [
            "name", "price", "image", "stock_quantity", "category",
            "color", "model_number", "brand", "description",
        ]
        self.assertEqual(list(form.fields.keys()), expected)

    def test_form_invalid_without_required_fields(self):
        form = ProductForm(data={})
        self.assertFalse(form.is_valid())
        # All fields should have errors (image handled separately)
        self.assertGreater(len(form.errors), 0)
