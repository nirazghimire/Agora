from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ProfileEditForm

"""Display the logged-in user's profile."""
@login_required
def profile_view(request):    
    return render(request, 'users/profile.html', {'profile_user': request.user})

"""Edit the logged-in user's profile."""
@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')
    else:
        form = ProfileEditForm(instance=request.user)

    return render(request, 'users/profile_edit.html', {'form': form})
