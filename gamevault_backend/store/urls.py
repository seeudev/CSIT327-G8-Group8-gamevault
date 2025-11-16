"""
Simple URL patterns for the game store.
"""

from django.urls import path
from . import views
from .views import api_wishlist, api_wishlist_delete
from . import analytics_views

app_name = 'store'

urlpatterns = [
    # Public game browsing
    path('', views.game_list, name='game_list'),
    path('game/<int:game_id>/', views.game_detail, name='game_detail'),
    path('games/', views.game_list, name='game_list'),
    path('api/games/search/', views.game_search, name='game_search'),
    path('tag/<int:tag_id>/', views.games_by_tag, name='games_by_tag'),

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

    # Wishlist API endpoints (Module 10) - function-based views
    path('api/wishlist/', api_wishlist, name='api-wishlist'),
    path('api/wishlist/<int:game_id>/', api_wishlist_delete, name='api-wishlist-delete'),

    # Normal wishlist page (Module 10)
    path('wishlist/', views.wishlist, name='wishlist'),
    path('wishlist/remove/<int:game_id>/', views.wishlist_remove, name='wishlist_remove'),

    # Review API endpoints (Module 11)
    path('api/reviews/<int:game_id>/', views.api_get_game_reviews, name='api_get_game_reviews'),
    path('api/reviews/<int:game_id>/create/', views.api_create_review, name='api_create_review'),
    path('api/reviews/<int:review_id>/update/', views.api_update_review, name='api_update_review'),
    path('api/reviews/<int:review_id>/delete/', views.api_delete_review, name='api_delete_review'),
    path('api/reviews/<int:game_id>/stats/', views.api_get_game_rating_stats, name='api_get_game_rating_stats'),

    # Analytics endpoints (Module 15)
    path('admin/analytics/', analytics_views.analytics_dashboard, name='analytics_dashboard'),
    path('api/analytics/overview/', analytics_views.api_analytics_overview, name='api_analytics_overview'),
    path('api/analytics/sales-trend/', analytics_views.api_analytics_sales_trend, name='api_analytics_sales_trend'),
    path('api/analytics/user-engagement/', analytics_views.api_analytics_user_engagement, name='api_analytics_user_engagement'),
    path('api/analytics/top-games/', analytics_views.api_analytics_top_games, name='api_analytics_top_games'),
    path('api/analytics/category-performance/', analytics_views.api_analytics_category_performance, name='api_analytics_category_performance'),
    path('api/analytics/export/csv/', analytics_views.export_analytics_csv, name='export_analytics_csv'),
    path('api/analytics/export/json/', analytics_views.export_analytics_json, name='export_analytics_json'),
]
