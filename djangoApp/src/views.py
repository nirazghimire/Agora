import base64
import json
from django.shortcuts import render, redirect
from django.contrib import messages
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from django.contrib.auth import authenticate
from django.contrib.auth import login, logout as auth_logout, get_user_model
from django.contrib.auth.models import User
from datetime import datetime, timezone as timezone




def home(request):
    return render(request, 'home.html')


def buyer(request):
    return render(request,'buyer.html')


def signup_page(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = User.objects.create_user(
            username=username,
            password=password
        )

        return redirect('login')
    return render(request,'signup.html')


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
            return redirect('login_dash')
        #redirect to the sample_success page !
        
        messages.error(request, 'Invalid credentials.') 
        #if user login fails, the error message flashes and then renders the login page 

    return render(request, 'login.html')


# # the ultimate goal of the func is to simulate successful login and then send the refresh and the access token to the user side in a real world prod 


def dash_jwt(request):
    access = request.session.get('jwt_access')

    if not access:
        return redirect('login_jwt')

    """
    For a proper implementation, you would now verify the JWT access token and the user's permissions.
    If the JWT is invalid or expired, you would redirect to login or show an error.
    If the user does not have the right permissions, you would show an unauthorized error.
    """
    try:
        validated_token = AccessToken(access)
        user_id = validated_token['user_id']
        User = get_user_model()
        user = User.objects.get(id=user_id)
    except (TokenError, InvalidToken):
        messages.error(request, 'Access token has expired or is invalid.')
        return redirect('login_jwt')
    except Exception:
        messages.error(request, 'Could not validate token.')
        return redirect('login_jwt')

    #Decode payload without verifying (just for display)
    payload_b64 = access.split('.')[1]
    #Pad base64 if needed
    padding = (4 - len(payload_b64) % 4) % 4
    payload = json.loads(base64.b64decode(payload_b64 + ('=' * padding)))

    exp_dt = datetime.fromtimestamp(payload['exp'], tz=timezone.utc)
    iat_dt = datetime.fromtimestamp(payload['iat'], tz=timezone.utc)
    minutes_remaining = max(0, int((exp_dt - datetime.now(tz=timezone.utc)).total_seconds() // 60))

    return render(request, 'login_dash.html', {
        'username': user.username,
        'access_token': access,
        'refresh_token': request.session.get('jwt_refresh'),
        'payload': json.dumps(payload, indent=2),
        'exp': exp_dt.strftime('%Y-%m-%d %H:%M:%S UTC'),
        'iat': iat_dt.strftime('%Y-%m-%d %H:%M:%S UTC'),
        'minutes_remaining': minutes_remaining,
        'header': f'Authorization: Bearer {access}',
    })


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
    return redirect('login_jwt')