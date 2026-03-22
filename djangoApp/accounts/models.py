from django.db import models
from django.contrib.auth.models import User

# Create your models here.
# django model for seller/ database schema
class Product(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField() 
    image = models.ImageField(upload_to='images')
    
    def __str__(self):
        return self.title