from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
#UserAdmin is the default admin for User model ; we are inheriting it to add custom fields
from .models import User, Address, Buyer, Seller


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User admin with role and profile fields."""
    list_display = ('username', 'email', 'role', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    #these variables list_display,list_filter etc are defined within the BaseUserAdmin class
    #we are just overriding them to add custom fields

    # Add custom fields to the existing fieldsets
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Profile', {'fields': ('role', 'bio')}),
    )#affects user_edit form

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Profile', {'fields': ('role', 'email')}),
    )#affects user_create form

    actions = ['revoke_users', 'activate_users']

    @admin.action(description='Revoke selected users (set inactive)')
    def revoke_users(self, request, queryset):
        count = queryset.update(is_active=False)
        self.message_user(request, f'{count} user(s) have been revoked.')

    @admin.action(description='Activate selected users')
    def activate_users(self, request, queryset):
        count = queryset.update(is_active=True)
        self.message_user(request, f'{count} user(s) have been activated.')


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'street', 'state', 'country', 'zip_code')
    search_fields = ('street', 'state', 'country')

