from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'image', 'stock_quantity', 'category', 'color', 'model_number', 'brand', 'description']
