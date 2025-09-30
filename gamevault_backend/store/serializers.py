from rest_framework import serializers
from .models import Game, GameKey, Order, OrderItem

class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ['id', 'title', 'description', 'price', 'platform', 'genre', 
                  'publisher', 'release_date', 'cover_image_url', 'is_active', 
                  'stock_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class GameKeySerializer(serializers.ModelSerializer):
    game_title = serializers.CharField(source='game.title', read_only=True)
    
    class Meta:
        model = GameKey
        fields = ['id', 'game', 'game_title', 'key_code', 'status', 
                  'created_at', 'sold_at']
        read_only_fields = ['id', 'created_at', 'sold_at']

class OrderItemSerializer(serializers.ModelSerializer):
    game_title = serializers.CharField(source='game.title', read_only=True)
    game_platform = serializers.CharField(source='game.platform', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'game', 'game_title', 'game_platform', 'price', 
                  'game_key', 'created_at']
        read_only_fields = ['id', 'created_at']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'user', 'user_username', 'total_amount', 'status', 
                  'items', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

class CreateOrderSerializer(serializers.Serializer):
    game_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False
    )
    
    def validate_game_ids(self, value):
        if not value:
            raise serializers.ValidationError("At least one game must be selected")
        return value
