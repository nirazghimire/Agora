import base64
import json
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_POST
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth import login, logout as auth_logout, get_user_model
from datetime import datetime, timezone as timezone
from users.models import Address


User = get_user_model()
from listings.models import Product



def home(request):
    if request.user.is_authenticated and getattr(request.user, 'role', '') == 'admin':
        return redirect('admin_dashboard')

    if request.user.is_authenticated and getattr(request.user, 'is_seller', False):
        products = Product.objects.filter(seller=request.user).order_by('-id')
        is_seller_view = True
    else:
        # Only show products from active sellers that are approved
        products = Product.objects.filter(is_approved=True, seller__is_active=True).order_by('-id')
        is_seller_view = False
    return render(request, 'home/index.html', 
                  {'products': products, 'is_seller_view': is_seller_view})

    #note : render has three layers of inputs: a request object(carries metadata like user,session, headers),html template to render, and the context-- the dict(the varialbes to be passed to the template) ; the keys are the varialbes passed onto the templates and the values of the dict are the actual data passed to render in the UI;



def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        role = request.POST.get('role')
        bio = request.POST.get('bio')
        country = request.POST.get('country', '').strip()
        state = request.POST.get('state', '').strip()
        street = request.POST.get('street', '').strip()
        zip_code = request.POST.get('zip_code', '').strip()

        if not username or not email or not password:
            messages.error(request, 'Username, email, and password are required.')
            return render(request, 'users/signup.html')

        if len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return render(request, 'users/signup.html')

        if role == 'buyer' and (not country or not state or not street or not zip_code):
            messages.error(request, 'Address details are required for buyer accounts.')
            return render(request, 'users/signup.html')

        if zip_code and not zip_code.isdigit():
            messages.error(request, 'Zip code must contain digits only.')
            return render(request, 'users/signup.html')

        if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
            messages.error(request, 'Either the username or email is already taken.')
            return render(request, 'users/signup.html')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role = role,
            bio = bio
        )

        if country and state and street and zip_code:
            Address.objects.create(
                user=user,
                country=country,
                state=state,
                street=street,
                zip_code=int(zip_code),
            )

        return redirect('home')
    return render(request,'users/signup.html')


def login_jwt(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        # how does authenticate work ??

        if user:
            # Check if user is banned (is_active = False)
            if not user.is_active:
                messages.error(request, 'Your account has been banned. Please contact support.')
                return render(request, 'users/signin.html')
            
            # Check if user is approved (is_approved = False implies pending admin approval)
            if not user.is_approved and not user.is_superuser and getattr(user, 'role', '') != 'admin':
                messages.error(request, 'Your account is pending admin approval. Please wait until an admin approves your registration.')
                return render(request, 'users/signin.html')
            
            # Establish Django session authentication
            login(request, user)
            refresh = RefreshToken.for_user(user)
            access = str(refresh.access_token)

            #Store tokens in session to simulate client-side storage. 
            #In a real implementation, the access token and refresh token would be sent to the client and stored there as a cookie.

            """in prod level implementation, there is no server-side session storage or anything ; implementing jwt is absolutely stateless for servers and 
            sits all on the client side """

            request.session['jwt_access'] = access
            request.session['jwt_refresh'] = str(refresh)
            request.session['jwt_username'] = username

            if getattr(user, 'role', '') == 'admin':
                return redirect('admin_dashboard')
            return redirect('home')
        #redirect to the sample_success page !
        
        messages.error(request, 'Invalid credentials.') 
        #if user login fails, the error message flashes and then renders the login page 
        
    #if the request is GET ; 
    return render(request, 'users/signin.html')


def forgot_password(request):
    """Reset a user's password using their username."""
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        new_password = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not username or not new_password or not confirm_password:
            messages.error(request, 'All fields are required.')
            return render(request, 'users/forgot_password.html')

        if new_password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'users/forgot_password.html')

        if len(new_password) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return render(request, 'users/forgot_password.html')

        user = User.objects.filter(username=username).first()
        if not user:
            messages.error(request, 'No account found with that username.')
            return render(request, 'users/forgot_password.html')

        user.set_password(new_password)
        user.save(update_fields=['password'])
        messages.success(request, 'Password reset successful. Please sign in with your new password.')
        return redirect('login')

    return render(request, 'users/forgot_password.html')


#the decorator restricts the logout to POST and does not trigger on GET
@require_POST
def logout_jwt(request):
    # Reset cart contents on logout so next login starts with an empty cart.
    if request.user.is_authenticated:
        try:
            request.user.cart.items.all().delete()
        except Exception:
            pass

    # Clear Django auth session
    auth_logout(request)

    #Try to blacklist the refresh token
    refresh_token = request.session.get('jwt_refresh')
    if refresh_token:
        try:
            RefreshToken(refresh_token).blacklist()
        except Exception:
            #Something went wrong.
            pass #Do nothing, not recommended for an error case.

    request.session.pop('jwt_access', None)
    request.session.pop('jwt_refresh', None)
    request.session.pop('jwt_username', None)

    #Go to login page
    return redirect('home')
# the redirect function takes internal name set in the urls of the django
