from PIL.IcnsImagePlugin import read_png_or_jpeg2000
from rest_framework import serializers
from django.core.exceptions import ValidationError
from django.core.validators import validate_image_file_extension
from .models import Game, Wishlist
# from .models import Game, GameKey, GameCategory, Wishlist


# class GameCategorySerializer(serializers.ModelSerializer):
#     """
#     Serializer for GameCategory model.
#     Used for displaying category information in API responses.
#     """
#     class Meta:
#         model = GameCategory
#         fields = ['id', 'name', 'description', 'icon', 'color', 'slug', 'is_active', 'created_at']
#         read_only_fields = ['id', 'slug', 'created_at']
#
#
# class GameKeySerializer(serializers.ModelSerializer):
#     """
#     Serializer for GameKey model.
#     Used for managing individual game keys.
#     """
#     class Meta:
#         model = GameKey
#         fields = [
#             'id', 'key', 'status', 'platform', 'region',
#             'created_at', 'sold_at', 'sold_to'
#         ]
#         read_only_fields = ['id', 'created_at', 'sold_at', 'sold_to']
#
#     def validate_key(self, value):
#         """Validate that the key is unique"""
#         if GameKey.objects.filter(key=value).exists():
#             raise serializers.ValidationError("A game key with this value already exists.")
#         return value


class GameListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing games (admin view).
    Shows essential game information for admin panels.
    """
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    updated_by_username = serializers.CharField(source='updated_by.username', read_only=True)
    cover_image_url = serializers.CharField(source='cover_image_url', read_only=True)
    is_on_sale = serializers.BooleanField(read_only=True)
    discount_percentage = serializers.IntegerField(read_only=True)
    is_in_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = Game
        fields = [
            'id', 'title', 'slug', 'price', 'original_price', 'status',
            'genre', 'developer', 'publisher', 'release_date',
            'stock_quantity', 'total_sold', 'average_rating', 'total_reviews',
            'featured', 'is_on_sale', 'discount_percentage', 'is_in_stock',
            'cover_image', 'cover_image_url', 'created_by_username',
            'updated_by_username', 'created_at', 'updated_at'
        ]


class GameDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed game information.
    Used for full game CRUD operations.
    """
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    updated_by_username = serializers.CharField(source='updated_by.username', read_only=True)
    cover_image_url = serializers.CharField(source='cover_image_url', read_only=True)
    is_on_sale = serializers.BooleanField(read_only=True)
    discount_percentage = serializers.IntegerField(read_only=True)
    is_in_stock = serializers.BooleanField(read_only=True)
    # keys = GameKeySerializer(many=True, read_only=True)

    class Meta:
        model = Game
        fields = [
            'id', 'title', 'slug', 'description', 'short_description',
            'price', 'original_price', 'cover_image', 'cover_image_url',
            'screenshots', 'trailer_url', 'developer', 'publisher',
            'release_date', 'genre', 'tags', 'minimum_requirements',
            'recommended_requirements', 'platforms', 'status',
            'stock_quantity', 'total_sold', 'average_rating', 'total_reviews',
            'meta_description', 'featured', 'is_on_sale', 'discount_percentage',
            'is_in_stock', 'keys', 'created_by_username', 'updated_by_username',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'slug', 'created_by_username', 'updated_by_username',
            'cover_image_url', 'is_on_sale', 'discount_percentage', 'is_in_stock',
            'keys', 'created_at', 'updated_at'
        ]

    def validate_cover_image(self, value):
        """Validate cover image file"""
        if value:
            validate_image_file_extension(value)
            # Check file size (max 5MB)
            if value.size > 5 * 1024 * 1024:
                raise serializers.ValidationError("Image file too large. Maximum size is 5MB.")
        return value

    def validate_price(self, value):
        """Validate price is positive"""
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0.")
        return value

    def validate_original_price(self, value):
        """Validate original price is positive and greater than current price"""
        if value is not None:
            if value <= 0:
                raise serializers.ValidationError("Original price must be greater than 0.")
            # Check if original price is greater than current price
            current_price = self.initial_data.get('price')
            if current_price and value <= current_price:
                raise serializers.ValidationError("Original price must be greater than current price for sale items.")
        return value

    def validate_screenshots(self, value):
        """Validate screenshots list"""
        if value and len(value) > 10:
            raise serializers.ValidationError("Maximum 10 screenshots allowed.")
        return value

    def validate_tags(self, value):
        """Validate tags list"""
        if value and len(value) > 20:
            raise serializers.ValidationError("Maximum 20 tags allowed.")
        return value

    def validate_platforms(self, value):
        """Validate platforms list"""
        if not value:
            raise serializers.ValidationError("At least one platform must be specified.")
        valid_platforms = ['Windows', 'Mac', 'Linux', 'PlayStation', 'Xbox', 'Nintendo Switch']
        for platform in value:
            if platform not in valid_platforms:
                raise serializers.ValidationError(f"Invalid platform: {platform}. Valid platforms are: {', '.join(valid_platforms)}")
        return value

    def create(self, validated_data):
        """Create a new game with audit fields"""
        request = self.context.get('request')
        if request and request.user:
            validated_data['created_by'] = request.user
            validated_data['updated_by'] = request.user
        
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Update game with audit fields"""
        request = self.context.get('request')
        if request and request.user:
            validated_data['updated_by'] = request.user
        
        return super().update(instance, validated_data)


class GameCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new games.
    Simplified version for game creation forms.
    """
    class Meta:
        model = Game
        fields = [
            'title', 'description', 'short_description', 'price', 'original_price',
            'cover_image', 'screenshots', 'trailer_url', 'developer', 'publisher',
            'release_date', 'genre', 'tags', 'minimum_requirements',
            'recommended_requirements', 'platforms', 'status', 'stock_quantity',
            'meta_description', 'featured'
        ]

    def validate_cover_image(self, value):
        """Validate cover image file"""
        if value:
            validate_image_file_extension(value)
            if value.size > 5 * 1024 * 1024:
                raise serializers.ValidationError("Image file too large. Maximum size is 5MB.")
        return value

    def validate_price(self, value):
        """Validate price is positive"""
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0.")
        return value

    def validate_original_price(self, value):
        """Validate original price"""
        if value is not None and value <= 0:
            raise serializers.ValidationError("Original price must be greater than 0.")
        return value

    def create(self, validated_data):
        """Create a new game with audit fields"""
        request = self.context.get('request')
        if request and request.user:
            validated_data['created_by'] = request.user
            validated_data['updated_by'] = request.user
        
        return super().create(validated_data)


class GameUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating existing games.
    Allows partial updates of game fields.
    """
    class Meta:
        model = Game
        fields = [
            'title', 'description', 'short_description', 'price', 'original_price',
            'cover_image', 'screenshots', 'trailer_url', 'developer', 'publisher',
            'release_date', 'genre', 'tags', 'minimum_requirements',
            'recommended_requirements', 'platforms', 'status', 'stock_quantity',
            'meta_description', 'featured'
        ]

    def validate_cover_image(self, value):
        """Validate cover image file"""
        if value:
            validate_image_file_extension(value)
            if value.size > 5 * 1024 * 1024:
                raise serializers.ValidationError("Image file too large. Maximum size is 5MB.")
        return value

    def validate_price(self, value):
        """Validate price is positive"""
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0.")
        return value

    def validate_original_price(self, value):
        """Validate original price"""
        if value is not None and value <= 0:
            raise serializers.ValidationError("Original price must be greater than 0.")
        return value

    def update(self, instance, validated_data):
        """Update game with audit fields"""
        request = self.context.get('request')
        if request and request.user:
            validated_data['updated_by'] = request.user
        
        return super().update(instance, validated_data)


class GamePublicSerializer(serializers.ModelSerializer):
    """
    Serializer for public game information.
    Used for storefront display (no sensitive admin data).
    """
    cover_image_url = serializers.CharField(source='cover_image_url', read_only=True)
    is_on_sale = serializers.BooleanField(read_only=True)
    discount_percentage = serializers.IntegerField(read_only=True)
    is_in_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = Game
        fields = [
            'id', 'title', 'slug', 'description', 'short_description',
            'price', 'original_price', 'cover_image_url', 'screenshots',
            'trailer_url', 'developer', 'publisher', 'release_date',
            'genre', 'tags', 'platforms', 'average_rating', 'total_reviews',
            'is_on_sale', 'discount_percentage', 'is_in_stock', 'featured'
        ]


# class GameKeyCreateSerializer(serializers.ModelSerializer):
#     """
#     Serializer for creating game keys.
#     Used for bulk key creation.
#     """
#     class Meta:
#         model = GameKey
#         fields = ['key', 'platform', 'region']
#
#     def validate_key(self, value):
#         """Validate that the key is unique"""
#         if GameKey.objects.filter(key=value).exists():
#             raise serializers.ValidationError("A game key with this value already exists.")
#         return value
#
#     def create(self, validated_data):
#         """Create a new game key"""
#         game = self.context.get('game')
#         if game:
#             validated_data['game'] = game
#         return super().create(validated_data)


# class GameKeyBulkCreateSerializer(serializers.Serializer):
#     """
#     Serializer for bulk creating game keys.
#     Accepts a list of keys to create for a specific game.
#     """
#     keys = serializers.ListField(
#         child=serializers.CharField(max_length=200),
#         min_length=1,
#         max_length=100
#     )
#     platform = serializers.CharField(max_length=50, required=False, allow_blank=True)
#     region = serializers.CharField(max_length=50, required=False, allow_blank=True)
#
#     def validate_keys(self, value):
#         """Validate that all keys are unique"""
#         existing_keys = GameKey.objects.filter(key__in=value).values_list('key', flat=True)
#         if existing_keys:
#             raise serializers.ValidationError(f"Keys already exist: {', '.join(existing_keys)}")
#         return value
#
#     def create(self, validated_data):
#         """Create multiple game keys"""
#         game = self.context.get('game')
#         keys_data = validated_data['keys']
#         platform = validated_data.get('platform', '')
#         region = validated_data.get('region', '')
#
#         game_keys = []
#         for key_value in keys_data:
#             game_key = GameKey.objects.create(
#                 game=game,
#                 key=key_value,
#                 platform=platform,
#                 region=region
#             )
#             game_keys.append(game_key)
#
#         return game_keys


class WishlistSerializer(serializers.ModelSerializer):
    game_title = serializers.CharField(source='game.title', read_only=True)
    game_thumbnail = serializers.ImageField(source='game.thumbnail', read_only=True)

    class Meta:
        model = Wishlist
        fields = ['id', 'user', 'game', 'game_title', 'game_thumbnail', 'added_at']
        read_only_fields = ['user', 'added_at']

