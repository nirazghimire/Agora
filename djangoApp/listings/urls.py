from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_listing, name='create_listing'),
    path('search-ajax/', views.search_products_ajax, name='search_products_ajax'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('product/<int:product_id>/quickview/', views.product_quickview, name='product_quickview'),
    path('product/<int:product_id>/review/', views.submit_review, name='submit_review'),
    path('reviews/', views.seller_reviews, name='seller_reviews'),
]
