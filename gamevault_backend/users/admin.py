"""
Simple admin configuration for User model.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Admin interface for custom User model.
    """
    list_display = ['username', 'email', 'is_admin', 'is_active', 'registration_date']
    list_filter = ['is_admin', 'is_active', 'is_staff', 'is_superuser']
    search_fields = ['username', 'email']
    ordering = ['-registration_date']
    
    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        ('Personal Info', {
            'fields': ('email',)
        }),
        ('Permissions', {
            'fields': ('is_admin', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined', 'registration_date')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_admin'),
        }),
    )
    
    readonly_fields = ['registration_date', 'last_login', 'date_joined']
