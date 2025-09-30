from django.contrib import admin
from .models import Game, GameKey, Order, OrderItem

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ['title', 'platform', 'price', 'stock_count', 'is_active', 'created_at']
    list_filter = ['platform', 'is_active', 'genre']
    search_fields = ['title', 'publisher']

@admin.register(GameKey)
class GameKeyAdmin(admin.ModelAdmin):
    list_display = ['game', 'status', 'created_at', 'sold_at']
    list_filter = ['status', 'game']
    search_fields = ['key_code', 'game__title']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'total_amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'user__email']

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'game', 'price', 'game_key', 'created_at']
    list_filter = ['created_at']
    search_fields = ['game__title', 'order__user__username']
