import base64
import json
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_POST
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from django.contrib.auth import authenticate
from django.contrib.auth import login, logout as auth_logout, get_user_model
from django.contrib.auth.models import User
from datetime import datetime, timezone as timezone




def home(request):
    return render(request, 'home/base.html')


def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = User.objects.create_user(
            username=username,
            password=password
        )

        return redirect('home')
    return render(request,'home/signup.html')


def login_jwt(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        # how does authenticate work ??

        if user:
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
            return redirect('home')
        #redirect to the sample_success page !
        
        messages.error(request, 'Invalid credentials.') 
        #if user login fails, the error message flashes and then renders the login page 

    return render(request, 'home/signin.html')

#the decorator restricts the logout to POST and does not trigger on GET
@require_POST
def logout_jwt(request):
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
