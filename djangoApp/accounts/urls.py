from django.urls import path
from . import views


urlpatterns = [
        path("login/",views.login_jwt,name="login"),
        path("forgot-password/",views.forgot_password,name="forgot_password"),
        path("signup/",views.signup,name="sign_up"),
        path("logout/",views.logout_jwt,name="logout"), # this logout path is simply for the form in the base.html.
]
