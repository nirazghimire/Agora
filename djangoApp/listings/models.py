from django.db import models
import uuid
from django.core.exceptions import ValidationError
import os
import magic
from django.contrib.auth import get_user_model

User = get_user_model()
def upload_icon_to(_, filename): 
    #Leaving filenames as they are can be a risk, lets just rename them.
    extension = filename.rsplit('.', 1)[-1].lower()
    return f"products/{uuid.uuid4().hex}.{extension}"

ALLOWED_EXTENSIONS = ['.jpg', '.jpeg', '.png']
ALLOWED_MIME_TYPES = ['image/jpeg', 'image/png']

def validate_image_file(file):
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationError(f"Unsupported extension: {ext}. Use .jpg or .png")

    file.seek(0)
    mime = magic.from_buffer(file.read(2048), mime=True)
    file.seek(0)

    if mime not in ALLOWED_MIME_TYPES:
        raise ValidationError(f"File content is not a valid image (got {mime})")

# Create your models here.
class Product(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to=upload_icon_to,validators = [validate_image_file])
    stock_quantity = models.IntegerField()
    category = models.CharField(max_length=100)
    color = models.CharField(max_length=100)
    model_number = models.IntegerField()
    brand = models.CharField(max_length=100)
    description = models.TextField()
    