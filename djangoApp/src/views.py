from django.shortcuts import render
from rest_framework import viewsets
from .models import Product
from .serializers import ProductSerializer

def home(request):
    return render(request, 'home.html')


def buyer(request):
    return render(request,'buyer.html')

def login(request):
    return render(request,'login.html')

def seller(request):
    #grab all products from the database table
    all_products = Product.objects.all()
    context = {
        'products': all_products  
    }
    return render(request,'seller.html',context)

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer