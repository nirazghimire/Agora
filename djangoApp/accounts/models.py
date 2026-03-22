from django.db import models
from django.conf import settings

# Create your models here.
# django model for seller/ database schema
class Product(models.Model):
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField() 
    image = models.ImageField(upload_to='images')
    
    def __str__(self):
        return self.title