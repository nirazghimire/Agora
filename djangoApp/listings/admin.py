from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'seller', 'price', 'stock_quantity', 'is_approved')
    list_filter = ('is_approved', 'category')
    search_fields = ('name', 'description')
    list_editable = ('is_approved',)

