from django.db import models


class User(models.Model):
    ROLE_CHOICES = [
        ('buyer', 'Buyer'),
        ('seller', 'Seller'),
        ('admin', 'Admin'),
    ]
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    role = models.CharField(max_length=10,choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.name} ({self.role})"
    #this method now makes sure whenver object is called in the program, above is returned ; 
    
class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    #simpley foreign key means one user could have multiple addresses
    country = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    street = models.CharField(max_length=255)
    zip_code = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.street}, {self.state}, {self.country}"


class Buyer(models.Model):
    VERIFICATION_CHOICES = [
        ('unverified', 'Unverified'),
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('suspended', 'Suspended'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='buyer_profile')
    #onetoone field means one buyer to one user ;
    total_purchases = models.IntegerField(default=0)
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_CHOICES, default='unverified')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.name} (Buyer)"


class Seller(models.Model):
    VERIFICATION_CHOICES = [
        ('unverified', 'Unverified'),
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('suspended', 'Suspended'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='seller_profile')
    # one seller to one user
    store_name = models.CharField(max_length=255)
    total_sales = models.IntegerField(default=0)
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_CHOICES, default='unverified')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.store_name} ({self.user.name})"









