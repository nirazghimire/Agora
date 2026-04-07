from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ProductForm

@login_required
def create_listing(request):
    if not getattr(request.user, 'is_seller', False):
        messages.error(request, 'Only sellers can create listings.')
        return redirect('home')
        
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            # is_approved defaults to False
            product.save()
            messages.success(request, 'Listing created successfully! It will be visible once approved by an admin.')
            return redirect('home')
    else:
        form = ProductForm()
        
    return render(request, 'listings/create_listing.html', {'form': form})
