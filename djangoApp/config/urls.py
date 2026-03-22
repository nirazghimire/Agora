"""
URL configuration for app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from src import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'products', views.ProductViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.home,name='home'),         # name is for the internal use by django itself; 
    path('',include('src.urls')),
    path('buyer/',views.buyer,name='buyer'),
    path('api/',include(router.urls)),
    path('seller/',views.seller,name='seller'),
    path('seller/add-product/',views.create_product,name='create_product'),
    path('seller/edit-product/<int:product_id>/',views.edit_product,name='edit_product'),
    path('seller/delete-product/<int:product_id>/',views.delete_product,name='delete_product'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
