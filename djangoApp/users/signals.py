from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Buyer, Seller


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Auto-create Buyer or Seller profile when a new User is created."""
    if created:
        if instance.role == 'buyer':
            Buyer.objects.create(user=instance)
        elif instance.role == 'seller':
            Seller.objects.create(user=instance, store_name=f"{instance.username}'s Store")
