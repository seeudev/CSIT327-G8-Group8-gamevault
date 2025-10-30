"""
Simple URL patterns for the game store.
"""

from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    # Public game browsing
    path('', views.game_list, name='game_list'),
    path('game/<int:game_id>/', views.game_detail, name='game_detail'),
    
    # Shopping cart
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:game_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_quantity, name='update_cart_quantity'),
    
    # Checkout and transactions
    path('checkout/', views.checkout, name='checkout'),
    path('transactions/', views.transaction_history, name='transaction_history'),
    path('transactions/<int:transaction_id>/', views.transaction_detail, name='transaction_detail'),
    path('transactions/<int:transaction_id>/items/<int:item_id>/send-key/', views.send_game_key, name='send_game_key'),
    path('download/<int:transaction_id>/<int:game_id>/', views.download_game, name='download_game'),
    
    # Admin views
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/games/', views.admin_game_list, name='admin_game_list'),
    path('admin/games/create/', views.admin_game_create, name='admin_game_create'),
    path('admin/games/edit/<int:game_id>/', views.admin_game_edit, name='admin_game_edit'),
    path('admin/games/delete/<int:game_id>/', views.admin_game_delete, name='admin_game_delete'),
    path('admin/users/', views.admin_users_page, name='admin_users'),
    path('admin/transactions/', views.admin_transactions_page, name='admin_transactions'),
    
    # Admin API endpoints (Module 7)
    path('api/admin/stats/', views.api_admin_dashboard_stats, name='api_admin_stats'),
    path('api/users/', views.api_admin_users, name='api_admin_users'),
    path('api/transactions/', views.api_admin_transactions, name='api_admin_transactions'),
    
    # Review API endpoints (Module 11)
    path('api/reviews/<int:game_id>/', views.api_get_game_reviews, name='api_get_game_reviews'),
    path('api/reviews/<int:game_id>/create/', views.api_create_review, name='api_create_review'),
    path('api/reviews/<int:review_id>/update/', views.api_update_review, name='api_update_review'),
    path('api/reviews/<int:review_id>/delete/', views.api_delete_review, name='api_delete_review'),
    path('api/reviews/<int:game_id>/stats/', views.api_get_game_rating_stats, name='api_get_game_rating_stats'),
]
