from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets
from .models import Product
from .serializers import ProductSerializer
from .forms import ProductForm

def home(request):
    return render(request, 'home.html')


def buyer(request):
    return render(request,'buyer.html')

def login(request):
    return render(request,'login.html')

@login_required
def seller(request):
    #grab all products from the database table for this specific seller
    all_products = Product.objects.filter(seller=request.user)
    context = {
        'products': all_products  
    }
    return render(request,'seller.html',context)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

@login_required
def create_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST,request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()
            return redirect('seller')
    else:
        form = ProductForm()
    return render(request,'create_product.html',{'form':form}) 

@login_required
def edit_product(request,product_id):
    product = get_object_or_404(Product,id=product_id, seller=request.user)
    if request.method == 'POST':
        form = ProductForm(request.POST,request.FILES,instance=product)
        if form.is_valid():
            form.save()
            return redirect('seller')
    else:
        form = ProductForm(instance=product)
    return render(request,'edit_product.html',{'form':form})

@login_required
def delete_product(request,product_id):
    product = get_object_or_404(Product,id=product_id, seller=request.user)
    product.delete()
    return redirect('seller')
