"""
Admin URL configuration
"""
from django.urls import path
from . import admin_views

app_name = 'admin'

urlpatterns = [
    path('', admin_views.admin_dashboard, name='dashboard'),
    path('games/', admin_views.game_list, name='game_list'),
    path('games/new/', admin_views.game_create, name='game_create'),
    path('games/<slug:slug>/edit/', admin_views.game_edit, name='game_edit'),
    path('users/', admin_views.user_list, name='user_list'),
    path('orders/', admin_views.order_list, name='order_list'),
]

