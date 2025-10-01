"""
Simple URL configuration for GameVault project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    # Django admin (for superuser management)
    path('django-admin/', admin.site.urls),
    
    # Redirect root to game store
    path('', RedirectView.as_view(pattern_name='store:game_list', permanent=False)),
    
    # User authentication
    path('auth/', include('users.urls')),
    
    # Store (games, cart, checkout, admin)
    path('store/', include('store.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
