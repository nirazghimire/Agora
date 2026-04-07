"""Tests for users.models — User, Address, Buyer, Seller."""
from django.test import TestCase
from users.models import User, Address, Buyer, Seller


class UserModelTests(TestCase):
    """Tests for the custom User model."""

    def test_create_buyer_user(self):
        user = User.objects.create_user(
            username="buyer1", password="testpass123", role="buyer"
        )
        self.assertEqual(user.role, "buyer")
        self.assertTrue(user.is_buyer)
        self.assertFalse(user.is_seller)

    def test_create_seller_user(self):
        user = User.objects.create_user(
            username="seller1", password="testpass123", role="seller"
        )
        self.assertEqual(user.role, "seller")
        self.assertTrue(user.is_seller)
        self.assertFalse(user.is_buyer)

    def test_create_admin_user(self):
        user = User.objects.create_user(
            username="admin1", password="testpass123", role="admin"
        )
        self.assertEqual(user.role, "admin")
        self.assertFalse(user.is_seller)
        self.assertFalse(user.is_buyer)

    def test_str_representation(self):
        user = User.objects.create_user(
            username="alice", password="testpass123", role="buyer"
        )
        self.assertEqual(str(user), "alice (buyer)")

    def test_bio_blank_by_default(self):
        user = User.objects.create_user(
            username="bob", password="testpass123", role="buyer"
        )
        self.assertEqual(user.bio, "")

    def test_bio_can_be_set(self):
        user = User.objects.create_user(
            username="charlie", password="testpass123", role="seller", bio="Hi there"
        )
        self.assertEqual(user.bio, "Hi there")

    def test_created_at_auto_set(self):
        user = User.objects.create_user(
            username="dave", password="testpass123", role="buyer"
        )
        self.assertIsNotNone(user.created_at)


class AddressModelTests(TestCase):
    """Tests for the Address model."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="addruser", password="testpass123", role="buyer"
        )

    def test_create_address(self):
        addr = Address.objects.create(
            user=self.user,
            country="USA",
            state="TX",
            street="123 Main St",
            zip_code=75001,
        )
        self.assertEqual(addr.country, "USA")
        self.assertEqual(addr.zip_code, 75001)

    def test_str_representation(self):
        addr = Address.objects.create(
            user=self.user,
            country="USA",
            state="TX",
            street="123 Main St",
            zip_code=75001,
        )
        self.assertEqual(str(addr), "123 Main St, TX, USA")

    def test_user_can_have_multiple_addresses(self):
        Address.objects.create(
            user=self.user, country="USA", state="TX", street="Addr 1", zip_code=75001
        )
        Address.objects.create(
            user=self.user, country="USA", state="CA", street="Addr 2", zip_code=90001
        )
        self.assertEqual(self.user.addresses.count(), 2)

    def test_cascade_delete_with_user(self):
        Address.objects.create(
            user=self.user, country="USA", state="TX", street="Addr 1", zip_code=75001
        )
        self.user.delete()
        self.assertEqual(Address.objects.count(), 0)


class BuyerModelTests(TestCase):
    """Tests for the Buyer profile model."""

    def test_create_buyer_profile(self):
        user = User.objects.create_user(
            username="bprofile", password="testpass123", role="buyer"
        )
        # Signal should auto-create this, but test manual creation too
        Buyer.objects.filter(user=user).delete()
        buyer = Buyer.objects.create(user=user)
        self.assertEqual(buyer.total_purchases, 0)

    def test_str_representation(self):
        user = User.objects.create_user(
            username="bstr", password="testpass123", role="buyer"
        )
        buyer = user.buyer_profile
        self.assertEqual(str(buyer), "bstr (Buyer)")


class SellerModelTests(TestCase):
    """Tests for the Seller profile model."""

    def test_create_seller_profile(self):
        user = User.objects.create_user(
            username="sprofile", password="testpass123", role="seller"
        )
        seller = user.seller_profile
        self.assertEqual(seller.total_sales, 0)

    def test_str_representation(self):
        user = User.objects.create_user(
            username="sstr", password="testpass123", role="seller"
        )
        seller = user.seller_profile
        self.assertIn("sstr", str(seller))

    def test_cascade_delete_with_user(self):
        user = User.objects.create_user(
            username="sdel", password="testpass123", role="seller"
        )
        self.assertEqual(Seller.objects.filter(user=user).count(), 1)
        user.delete()
        self.assertEqual(Seller.objects.count(), 0)
