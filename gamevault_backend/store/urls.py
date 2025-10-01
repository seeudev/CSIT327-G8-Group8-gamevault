from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    # API Game management endpoints (admin only)
    path('api/games/', views.GameListView.as_view(), name='game-list'),
    path('api/games/<slug:slug>/', views.GameDetailView.as_view(), name='game-detail'),
    
    # API Public game endpoints (for storefront)
    path('api/public/games/', views.GamePublicListView.as_view(), name='game-public-list'),
    path('api/public/games/<slug:slug>/', views.GamePublicDetailView.as_view(), name='game-public-detail'),
    
    # API Game key management endpoints (admin only)
    path('api/games/<slug:game_slug>/keys/', views.GameKeyListView.as_view(), name='game-key-list'),
    path('api/games/<slug:game_slug>/keys/bulk/', views.GameKeyBulkCreateView.as_view(), name='game-key-bulk-create'),
    path('api/keys/<int:pk>/', views.GameKeyDetailView.as_view(), name='game-key-detail'),
    
    # API Game category management endpoints (admin only)
    path('api/categories/', views.GameCategoryListView.as_view(), name='game-category-list'),
    path('api/categories/<slug:slug>/', views.GameCategoryDetailView.as_view(), name='game-category-detail'),
    
    # API Admin dashboard endpoints
    path('api/stats/', views.game_stats, name='game-stats'),
    path('api/games/bulk-update-status/', views.bulk_update_game_status, name='bulk-update-game-status'),
    
    # Template-based views for vanilla HTML frontend
    path('', views.GameLibraryView.as_view(), name='game_library'),
    path('game/<slug:slug>/', views.GameDetailView.as_view(), name='game_detail'),
    path('cart/', views.CartView.as_view(), name='cart'),
    path('checkout/success/', views.CheckoutSuccessView.as_view(), name='checkout_success'),
]
