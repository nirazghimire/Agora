from django.urls import path
from . import views


urlpatterns = [
        path("login/",views.login_jwt,name="login"),
        path("login/login_dash/",views.dash_jwt,name="login_dash"),
        path("signup/",views.signup_page,name="sign_up"),
        path("logout/",views.logout_jwt,name="logout")
]