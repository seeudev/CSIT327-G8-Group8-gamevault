"""
Simple URL patterns for user authentication.
"""

from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    
    # Password reset URLs
    path('password-reset/request/', views.password_reset_request, name='password_reset_request'),
    path('password-reset/confirm/<str:token>/', views.password_reset_confirm, name='password_reset_confirm'),
    
    # API endpoints for profile management
    path('api/users/<int:user_id>/', views.update_profile_api, name='update_profile_api'),
    path('api/users/<int:user_id>/delete/', views.delete_account_api, name='delete_account_api'),
    
    # API endpoints for password reset
    path('api/password-reset/request/', views.password_reset_request, name='api_password_reset_request'),
    path('api/password-reset/confirm/<str:token>/', views.password_reset_confirm, name='api_password_reset_confirm'),
]
