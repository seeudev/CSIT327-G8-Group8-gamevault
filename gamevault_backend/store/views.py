from rest_framework import status, generics, permissions, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.db import models

from .models import Game, GameKey, GameCategory
from .serializers import (
    GameListSerializer,
    GameDetailSerializer,
    GameCreateSerializer,
    GameUpdateSerializer,
    GamePublicSerializer,
    GameKeySerializer,
    GameKeyCreateSerializer,
    GameKeyBulkCreateSerializer,
    GameCategorySerializer
)


class GameListView(generics.ListCreateAPIView):
    """
    List all games or create a new game.
    GET: List games (admin only)
    POST: Create new game (admin only)
    """
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'genre', 'featured', 'developer', 'publisher']
    search_fields = ['title', 'description', 'developer', 'publisher', 'tags']
    ordering_fields = ['title', 'price', 'release_date', 'created_at', 'average_rating']
    ordering = ['-created_at']
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        """Filter games based on user permissions"""
        user = self.request.user
        
        # Only admins can view all games
        if not user.is_admin:
            return Game.objects.none()
        
        return Game.objects.all().select_related('created_by', 'updated_by')

    def get_serializer_class(self):
        """Return appropriate serializer based on request method"""
        if self.request.method == 'POST':
            return GameCreateSerializer
        return GameListSerializer

    def perform_create(self, serializer):
        """Create game with audit fields"""
        serializer.save(
            created_by=self.request.user,
            updated_by=self.request.user
        )


class GameDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a game.
    GET: Get game details (admin only)
    PUT/PATCH: Update game (admin only)
    DELETE: Delete game (admin only)
    """
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'slug'
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        """Filter games based on user permissions"""
        user = self.request.user
        
        # Only admins can view/edit games
        if not user.is_admin:
            return Game.objects.none()
        
        return Game.objects.all().select_related('created_by', 'updated_by').prefetch_related('keys')

    def get_serializer_class(self):
        """Return appropriate serializer based on request method"""
        if self.request.method in ['PUT', 'PATCH']:
            return GameUpdateSerializer
        return GameDetailSerializer

    def perform_update(self, serializer):
        """Update game with audit fields"""
        serializer.save(updated_by=self.request.user)

    def destroy(self, request, *args, **kwargs):
        """Soft delete game by setting status to discontinued"""
        instance = self.get_object()
        instance.status = 'discontinued'
        instance.updated_by = request.user
        instance.save()
        
        return Response({
            'message': 'Game has been discontinued successfully'
        }, status=status.HTTP_200_OK)


class GamePublicListView(generics.ListAPIView):
    """
    List all active games for public storefront.
    GET: List active games (public access)
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = GamePublicSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['genre', 'featured', 'developer', 'publisher']
    search_fields = ['title', 'description', 'developer', 'publisher', 'tags']
    ordering_fields = ['title', 'price', 'release_date', 'average_rating']
    ordering = ['-featured', '-created_at']

    def get_queryset(self):
        """Return only active games for public view"""
        return Game.objects.filter(
            status='active'
        ).exclude(
            stock_quantity=0
        )


class GamePublicDetailView(generics.RetrieveAPIView):
    """
    Retrieve a single active game for public storefront.
    GET: Get game details (public access)
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = GamePublicSerializer
    lookup_field = 'slug'

    def get_queryset(self):
        """Return only active games for public view"""
        return Game.objects.filter(status='active')


class GameKeyListView(generics.ListCreateAPIView):
    """
    List all keys for a specific game or create new keys.
    GET: List game keys (admin only)
    POST: Create new game key (admin only)
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GameKeySerializer

    def get_queryset(self):
        """Filter keys based on user permissions and game"""
        user = self.request.user
        
        # Only admins can view game keys
        if not user.is_admin:
            return GameKey.objects.none()
        
        game_slug = self.kwargs.get('game_slug')
        return GameKey.objects.filter(
            game__slug=game_slug
        ).select_related('game', 'sold_to')

    def get_serializer_class(self):
        """Return appropriate serializer based on request method"""
        if self.request.method == 'POST':
            return GameKeyCreateSerializer
        return GameKeySerializer

    def perform_create(self, serializer):
        """Create game key with associated game"""
        game_slug = self.kwargs.get('game_slug')
        game = get_object_or_404(Game, slug=game_slug)
        serializer.save(game=game)


class GameKeyBulkCreateView(APIView):
    """
    Bulk create game keys for a specific game.
    POST: Create multiple game keys (admin only)
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, game_slug):
        """Create multiple game keys"""
        user = request.user
        
        # Only admins can create game keys
        if not user.is_admin:
            return Response({
                'error': 'Permission denied'
            }, status=status.HTTP_403_FORBIDDEN)

        game = get_object_or_404(Game, slug=game_slug)
        
        serializer = GameKeyBulkCreateSerializer(
            data=request.data,
            context={'game': game}
        )
        
        if serializer.is_valid():
            try:
                game_keys = serializer.save()
                
                # Update game stock quantity
                game.stock_quantity += len(game_keys)
                game.updated_by = user
                game.save()
                
                return Response({
                    'message': f'Successfully created {len(game_keys)} game keys',
                    'keys_created': len(game_keys),
                    'new_stock_quantity': game.stock_quantity
                }, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                return Response({
                    'error': 'Failed to create game keys',
                    'details': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'error': 'Invalid data',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class GameKeyDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a specific game key.
    GET: Get key details (admin only)
    PUT/PATCH: Update key (admin only)
    DELETE: Delete key (admin only)
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GameKeySerializer

    def get_queryset(self):
        """Filter keys based on user permissions"""
        user = self.request.user
        
        # Only admins can view/edit game keys
        if not user.is_admin:
            return GameKey.objects.none()
        
        return GameKey.objects.all().select_related('game', 'sold_to')


class GameCategoryListView(generics.ListCreateAPIView):
    """
    List all game categories or create a new category.
    GET: List categories (admin only)
    POST: Create new category (admin only)
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GameCategorySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def get_queryset(self):
        """Filter categories based on user permissions"""
        user = self.request.user
        
        # Only admins can manage categories
        if not user.is_admin:
            return GameCategory.objects.none()
        
        return GameCategory.objects.all()


class GameCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a game category.
    GET: Get category details (admin only)
    PUT/PATCH: Update category (admin only)
    DELETE: Delete category (admin only)
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GameCategorySerializer
    lookup_field = 'slug'

    def get_queryset(self):
        """Filter categories based on user permissions"""
        user = self.request.user
        
        # Only admins can view/edit categories
        if not user.is_admin:
            return GameCategory.objects.none()
        
        return GameCategory.objects.all()


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def game_stats(request):
    """
    Get game statistics for admin dashboard.
    Returns counts and metrics for games, keys, and sales.
    """
    user = request.user
    
    # Only admins can view game statistics
    if not user.is_admin:
        return Response({
            'error': 'Permission denied'
        }, status=status.HTTP_403_FORBIDDEN)

    try:
        # Game statistics
        total_games = Game.objects.count()
        active_games = Game.objects.filter(status='active').count()
        featured_games = Game.objects.filter(featured=True).count()
        out_of_stock = Game.objects.filter(stock_quantity=0).count()

        # Key statistics
        total_keys = GameKey.objects.count()
        available_keys = GameKey.objects.filter(status='available').count()
        sold_keys = GameKey.objects.filter(status='sold').count()

        # Sales statistics
        total_sales = GameKey.objects.filter(status='sold').count()
        total_revenue = sum(
            key.game.price for key in GameKey.objects.filter(status='sold')
        )

        # Genre distribution
        genre_stats = Game.objects.values('genre').annotate(
            count=models.Count('id')
        ).order_by('-count')[:10]

        return Response({
            'games': {
                'total': total_games,
                'active': active_games,
                'featured': featured_games,
                'out_of_stock': out_of_stock
            },
            'keys': {
                'total': total_keys,
                'available': available_keys,
                'sold': sold_keys
            },
            'sales': {
                'total_sales': total_sales,
                'total_revenue': float(total_revenue)
            },
            'genres': list(genre_stats)
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'error': 'Failed to fetch statistics',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def bulk_update_game_status(request):
    """
    Bulk update game status for multiple games.
    POST: Update status for multiple games (admin only)
    """
    user = request.user
    
    # Only admins can bulk update games
    if not user.is_admin:
        return Response({
            'error': 'Permission denied'
        }, status=status.HTTP_403_FORBIDDEN)

    game_ids = request.data.get('game_ids', [])
    new_status = request.data.get('status')

    if not game_ids or not new_status:
        return Response({
            'error': 'game_ids and status are required'
        }, status=status.HTTP_400_BAD_REQUEST)

    if new_status not in ['active', 'inactive', 'coming_soon', 'discontinued']:
        return Response({
            'error': 'Invalid status value'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        updated_count = Game.objects.filter(
            id__in=game_ids
        ).update(
            status=new_status,
            updated_by=user
        )

        return Response({
            'message': f'Successfully updated {updated_count} games',
            'updated_count': updated_count,
            'new_status': new_status
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'error': 'Failed to update games',
            'details': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
