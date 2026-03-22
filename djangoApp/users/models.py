from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    custom user model extending Django's AbstractUser ; inherits a lot of stuffs the most important
    being hashed password instead of custom User model storing passwords in plain text ;
    abstractUser has default fields such as username, first_name, email, last_name, password,is_active etc
    """
    ROLE_CHOICES = [
        ('buyer', 'Buyer'),
        ('seller', 'Seller'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    bio = models.TextField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} ({self.role})"

    @property
    def is_seller(self):
        return self.role == 'seller'

    @property
    def is_buyer(self):
        return self.role == 'buyer'

""" TO MAKE changes in the property over here"""


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    #simply foreign key means one user could have multiple addresses
    country = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    street = models.CharField(max_length=255)
    zip_code = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.street}, {self.state}, {self.country}"


class Buyer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='buyer_profile')
    #onetoone field means one buyer to one user ;
    total_purchases = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} (Buyer)"


class Seller(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='seller_profile')
    # one seller to one user
    store_name = models.CharField(max_length=255)
    total_sales = models.IntegerField(default=0)
    #essential for seller dashboard etc; 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.store_name} ({self.user.username})"
