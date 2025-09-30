from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.db import transaction
from django.utils import timezone
from .models import Game, GameKey, Order, OrderItem
from .serializers import (
    GameSerializer, GameKeySerializer, OrderSerializer, 
    OrderItemSerializer, CreateOrderSerializer
)

class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.filter(is_active=True)
    serializer_class = GameSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        platform = self.request.query_params.get('platform', None)
        genre = self.request.query_params.get('genre', None)
        
        if platform:
            queryset = queryset.filter(platform=platform)
        if genre:
            queryset = queryset.filter(genre__icontains=genre)
        
        return queryset

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """Create a new order with game purchases"""
        serializer = CreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        game_ids = serializer.validated_data['game_ids']
        games = Game.objects.filter(id__in=game_ids, is_active=True)
        
        if len(games) != len(game_ids):
            return Response(
                {"error": "Some games are not available"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check stock availability
        for game in games:
            available_keys = GameKey.objects.filter(
                game=game, 
                status='AVAILABLE'
            ).count()
            if available_keys < 1:
                return Response(
                    {"error": f"Game '{game.title}' is out of stock"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Calculate total
        total_amount = sum(game.price for game in games)
        
        # Check user balance
        if request.user.wallet_balance < total_amount:
            return Response(
                {"error": "Insufficient wallet balance"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create order
        order = Order.objects.create(
            user=request.user,
            total_amount=total_amount,
            status='COMPLETED'
        )
        
        # Create order items and assign keys
        for game in games:
            game_key = GameKey.objects.filter(
                game=game,
                status='AVAILABLE'
            ).first()
            
            game_key.status = 'SOLD'
            game_key.sold_at = timezone.now()
            game_key.save()
            
            OrderItem.objects.create(
                order=order,
                game=game,
                game_key=game_key,
                price=game.price
            )
            
            game.stock_count -= 1
            game.save()
        
        # Deduct from wallet
        request.user.wallet_balance -= total_amount
        request.user.save()
        
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def keys(self, request, pk=None):
        """Get game keys for a specific order"""
        order = self.get_object()
        items = order.items.all()
        keys_data = []
        
        for item in items:
            if item.game_key:
                keys_data.append({
                    'game_title': item.game.title,
                    'platform': item.game.platform,
                    'key_code': item.game_key.key_code
                })
        
        return Response(keys_data)
