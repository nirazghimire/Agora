from django.db import models
from users.models import User
import uuid
import os
import magic
from django.core.exceptions import ValidationError

# class Order(models.Model):
#     user = models.ForeignKey(User,on_delete=models.CASCADE)
#     total_cost = models.DecimalField()
#     created_at = models.DateTimeField()

def upload_image_to(_,filename):
    extension = filename.rsplit('.', 1)[-1].lower()
    return f"products/{uuid.uuid4().hex}.{extension}"
#renaming the file uploaded by the user ; best security practice!


ALLOWED_EXTENSIONS = ['.jpg', '.jpeg', '.png']
ALLOWED_MIME_TYPES = ['image/jpeg', 'image/png']

def validate_image_file(file):
    extension = os.path.splitext(file.name)[1].lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise ValidationError(f"Unsupported extension: {extension}. Use .jpg or .png")

    file.seek(0)
    mime = magic.from_buffer(file.read(2048), mime=True)
    file.seek(0)

    if mime not in ALLOWED_MIME_TYPES:
        raise ValidationError(f"File content is not a valid image (got {mime})")


class Product(models.Model):
    name = models.CharField(max_length=100)
    seller = models.ForeignKey(User)
    image = models.ImageField(upload_to=upload_image_to,validators=[validate_image_file])
    price = models.DecimalField()
    stock_qty = models.IntegerField()
    category = models.CharField(max_length=255)
    brand = models.CharField(max_length=100)
    model_number = models.IntegerField(unique=True)
    color = models.CharField(max_length=10)
    description = models.CharField(max_length=1000)





