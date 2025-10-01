from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    # Game management endpoints (admin only)
    path('games/', views.GameListView.as_view(), name='game-list'),
    path('games/<slug:slug>/', views.GameDetailView.as_view(), name='game-detail'),
    
    # Public game endpoints (for storefront)
    path('public/games/', views.GamePublicListView.as_view(), name='game-public-list'),
    path('public/games/<slug:slug>/', views.GamePublicDetailView.as_view(), name='game-public-detail'),
    
    # Game key management endpoints (admin only)
    path('games/<slug:game_slug>/keys/', views.GameKeyListView.as_view(), name='game-key-list'),
    path('games/<slug:game_slug>/keys/bulk/', views.GameKeyBulkCreateView.as_view(), name='game-key-bulk-create'),
    path('keys/<int:pk>/', views.GameKeyDetailView.as_view(), name='game-key-detail'),
    
    # Game category management endpoints (admin only)
    path('categories/', views.GameCategoryListView.as_view(), name='game-category-list'),
    path('categories/<slug:slug>/', views.GameCategoryDetailView.as_view(), name='game-category-detail'),
    
    # Admin dashboard endpoints
    path('stats/', views.game_stats, name='game-stats'),
    path('games/bulk-update-status/', views.bulk_update_game_status, name='bulk-update-game-status'),
]
