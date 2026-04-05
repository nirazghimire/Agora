from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    
    # Products
    path('admin-panel/pending-products/', views.pending_products, name='pending_products'),
    path('admin-panel/approved-products/', views.approved_products, name='approved_products'),
    path('admin-panel/approve-product/<int:product_id>/', views.approve_product, name='approve_product'),
    path('admin-panel/reject-product/<int:product_id>/', views.reject_product, name='reject_product'),
    path('admin-panel/revoke-product/<int:product_id>/', views.revoke_product, name='revoke_product'),
    
    # Sellers Management
    path('admin-panel/manage-sellers/', views.manage_sellers, name='manage_sellers'),
    path('admin-panel/ban-seller/<int:user_id>/', views.ban_user, name='ban_seller'),
    path('admin-panel/unban-seller/<int:user_id>/', views.unban_user, name='unban_seller'),
    
    # Buyers Management
    path('admin-panel/manage-buyers/', views.manage_buyers, name='manage_buyers'),
    path('admin-panel/ban-buyer/<int:user_id>/', views.ban_user, name='ban_buyer'),
    path('admin-panel/unban-buyer/<int:user_id>/', views.unban_user, name='unban_buyer'),
]
