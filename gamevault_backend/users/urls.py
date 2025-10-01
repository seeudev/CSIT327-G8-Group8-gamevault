from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView
)
from . import views

app_name = 'users'

urlpatterns = [
    # API Authentication endpoints
    path('api/register/', views.UserRegistrationView.as_view(), name='user-register'),
    path('api/login/', views.UserLoginView.as_view(), name='user-login'),
    path('api/logout/', views.LogoutView.as_view(), name='user-logout'),
    
    # JWT token endpoints
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),
    
    # API User profile endpoints
    path('api/profile/', views.UserProfileView.as_view(), name='user-profile'),
    path('api/change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    path('api/verify-token/', views.verify_token, name='verify-token'),
    
    # API User management endpoints (admin)
    path('api/list/', views.UserListView.as_view(), name='user-list'),
    
    # API Role endpoints
    path('api/roles/', views.RoleListView.as_view(), name='role-list'),
    path('api/permissions/', views.user_permissions, name='user-permissions'),
    
    # Template-based views for vanilla HTML frontend
    path('login/', views.LoginView.as_view(), name='login'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.home_view, name='home'),
    path('profile/', views.profile_view, name='profile'),
]
