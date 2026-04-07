"""Tests for users.signals — auto-create Buyer/Seller profiles."""
from django.test import TestCase
from users.models import User, Buyer, Seller


class UserSignalTests(TestCase):
    """Verify post_save signal creates correct profiles."""

    def test_buyer_profile_created_on_buyer_signup(self):
        user = User.objects.create_user(
            username="sigbuyer", password="testpass123", role="buyer"
        )
        self.assertTrue(Buyer.objects.filter(user=user).exists())
        self.assertFalse(Seller.objects.filter(user=user).exists())

    def test_seller_profile_created_on_seller_signup(self):
        user = User.objects.create_user(
            username="sigseller", password="testpass123", role="seller"
        )
        self.assertTrue(Seller.objects.filter(user=user).exists())
        self.assertFalse(Buyer.objects.filter(user=user).exists())

    def test_seller_store_name_auto_generated(self):
        user = User.objects.create_user(
            username="autostore", password="testpass123", role="seller"
        )
        seller = Seller.objects.get(user=user)
        self.assertEqual(seller.store_name, "autostore's Store")

    def test_no_profile_created_for_admin(self):
        user = User.objects.create_user(
            username="sigadmin", password="testpass123", role="admin"
        )
        self.assertFalse(Buyer.objects.filter(user=user).exists())
        self.assertFalse(Seller.objects.filter(user=user).exists())

    def test_signal_does_not_fire_on_update(self):
        user = User.objects.create_user(
            username="norefire", password="testpass123", role="buyer"
        )
        initial_count = Buyer.objects.count()
        user.bio = "updated"
        user.save()
        self.assertEqual(Buyer.objects.count(), initial_count)
