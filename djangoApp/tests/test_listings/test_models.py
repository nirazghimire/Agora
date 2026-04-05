"""Tests for listings.models — Product, upload_icon_to, validate_image_file."""
from django.test import TestCase
from listings.models import Product, upload_icon_to
from users.models import User


class UploadIconToTests(TestCase):
    """Tests for the upload_icon_to helper."""

    def test_generates_uuid_path(self):
        path = upload_icon_to(None, "photo.jpg")
        self.assertTrue(path.startswith("products/"))
        self.assertTrue(path.endswith(".jpg"))
        # UUID hex is 32 chars
        basename = path.split("/")[1].rsplit(".", 1)[0]
        self.assertEqual(len(basename), 32)

    def test_preserves_extension(self):
        self.assertTrue(upload_icon_to(None, "img.png").endswith(".png"))
        self.assertTrue(upload_icon_to(None, "img.JPEG").endswith(".jpeg"))


class ProductModelTests(TestCase):
    """Tests for the Product model."""

    def setUp(self):
        self.seller = User.objects.create_user(
            username="prodseller", password="testpass123", role="seller"
        )

    def test_is_approved_defaults_to_false(self):
        product = Product.objects.create(
            seller=self.seller, name="Gadget", price=50,
            stock_quantity=10, category="Tech", color="Blue",
            model_number=42, brand="Acme", description="Cool gadget",
            image="products/test.jpg",
        )
        self.assertFalse(product.is_approved)

    def test_product_fields(self):
        product = Product.objects.create(
            seller=self.seller, name="Gadget", price=99.99,
            stock_quantity=5, category="Tech", color="Red",
            model_number=7, brand="BrandX", description="Desc",
            image="products/test.jpg",
        )
        self.assertEqual(product.name, "Gadget")
        self.assertEqual(product.price, 99.99)
        self.assertEqual(product.stock_quantity, 5)

    def test_cascade_delete_with_seller(self):
        Product.objects.create(
            seller=self.seller, name="Gone", price=10,
            stock_quantity=1, category="A", color="B",
            model_number=1, brand="C", description="D",
            image="products/test.jpg",
        )
        self.seller.delete()
        self.assertEqual(Product.objects.count(), 0)
