from django.urls import path
from . import views

urlpatterns = [
    path('cart/', views.cart_detail, name='cart_detail'),
    path('checkout/', views.checkout, name='checkout'),
    path('orders/history/', views.purchase_history, name='purchase_history'),
    path('orders/sales/', views.sales_history, name='sales_history'),
    path('orders/returns/<int:order_item_id>/initiate/', views.initiate_return, name='initiate_return'),
    path('orders/returns/<int:return_request_id>/update/', views.update_return_request, name='update_return_request'),
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('increase/<int:product_id>/', views.increment_cart_item, name='increment_cart_item'),
    path('decrease/<int:product_id>/', views.decrement_cart_item, name='decrement_cart_item'),
    path('remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
]
