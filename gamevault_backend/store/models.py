from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
from decimal import Decimal

User = get_user_model()


class Game(models.Model):
    """
    Game model for storing digital game information.
    This model represents a game that can be sold in the GameVault store.
    """
    
    # Basic Information
    title = models.CharField(
        max_length=200,
        help_text="The title of the game"
    )
    description = models.TextField(
        help_text="Detailed description of the game"
    )
    short_description = models.CharField(
        max_length=500,
        blank=True,
        help_text="Brief description for cards and previews"
    )
    
    # Pricing
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Price of the game in USD"
    )
    original_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Original price before discount (for sale display)"
    )
    
    # Media
    cover_image = models.ImageField(
        upload_to='games/covers/',
        help_text="Main cover image for the game"
    )
    screenshots = models.JSONField(
        default=list,
        blank=True,
        help_text="List of screenshot URLs"
    )
    trailer_url = models.URLField(
        blank=True,
        null=True,
        help_text="YouTube or other video trailer URL"
    )
    
    # Game Details
    developer = models.CharField(
        max_length=100,
        help_text="Game developer company"
    )
    publisher = models.CharField(
        max_length=100,
        help_text="Game publisher company"
    )
    release_date = models.DateField(
        help_text="Official release date"
    )
    
    # Categories and Tags
    genre = models.CharField(
        max_length=50,
        help_text="Primary genre (e.g., Action, RPG, Strategy)"
    )
    tags = models.JSONField(
        default=list,
        blank=True,
        help_text="List of tags for filtering and search"
    )
    
    # System Requirements
    minimum_requirements = models.TextField(
        blank=True,
        help_text="Minimum system requirements"
    )
    recommended_requirements = models.TextField(
        blank=True,
        help_text="Recommended system requirements"
    )
    
    # Platform Support
    platforms = models.JSONField(
        default=list,
        help_text="Supported platforms (e.g., ['Windows', 'Mac', 'Linux'])"
    )
    
    # Game Status
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('coming_soon', 'Coming Soon'),
        ('discontinued', 'Discontinued'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        help_text="Current status of the game"
    )
    
    # Inventory and Sales
    stock_quantity = models.PositiveIntegerField(
        default=0,
        help_text="Number of keys available in stock"
    )
    total_sold = models.PositiveIntegerField(
        default=0,
        help_text="Total number of copies sold"
    )
    
    # Ratings and Reviews
    average_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('5.00'))],
        help_text="Average user rating (0.00 - 5.00)"
    )
    total_reviews = models.PositiveIntegerField(
        default=0,
        help_text="Total number of user reviews"
    )
    
    # SEO and Marketing
    slug = models.SlugField(
        max_length=200,
        unique=True,
        help_text="URL-friendly version of the title"
    )
    meta_description = models.CharField(
        max_length=160,
        blank=True,
        help_text="Meta description for SEO"
    )
    featured = models.BooleanField(
        default=False,
        help_text="Whether this game is featured on the homepage"
    )
    
    # Audit Fields
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_games',
        help_text="User who created this game entry"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='updated_games',
        help_text="User who last updated this game"
    )

    class Meta:
        db_table = 'games'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'featured']),
            models.Index(fields=['genre']),
            models.Index(fields=['price']),
            models.Index(fields=['average_rating']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return self.title

    @property
    def is_on_sale(self):
        """Check if the game is currently on sale"""
        return self.original_price and self.original_price > self.price

    @property
    def discount_percentage(self):
        """Calculate discount percentage if on sale"""
        if self.is_on_sale:
            return round(((self.original_price - self.price) / self.original_price) * 100)
        return 0

    @property
    def is_in_stock(self):
        """Check if the game is in stock"""
        return self.stock_quantity > 0

    @property
    def cover_image_url(self):
        """Get the full URL for the cover image"""
        if self.cover_image:
            return self.cover_image.url
        return None

    def save(self, *args, **kwargs):
        """Override save to auto-generate slug if not provided"""
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class GameKey(models.Model):
    """
    Model for storing individual game keys.
    Each Game can have multiple keys for sale.
    """
    
    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE,
        related_name='keys',
        help_text="The game this key belongs to"
    )
    key = models.CharField(
        max_length=200,
        unique=True,
        help_text="The actual game key/code"
    )
    
    # Key Status
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('sold', 'Sold'),
        ('reserved', 'Reserved'),
        ('invalid', 'Invalid'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='available',
        help_text="Current status of this key"
    )
    
    # Platform and Region
    platform = models.CharField(
        max_length=50,
        blank=True,
        help_text="Platform this key is for (e.g., Steam, Epic, Origin)"
    )
    region = models.CharField(
        max_length=50,
        blank=True,
        help_text="Region restriction (e.g., Global, US, EU)"
    )
    
    # Audit Fields
    created_at = models.DateTimeField(auto_now_add=True)
    sold_at = models.DateTimeField(null=True, blank=True)
    sold_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='purchased_keys',
        help_text="User who purchased this key"
    )

    class Meta:
        db_table = 'game_keys'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['game', 'status']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.game.title} - {self.key[:10]}..."


class GameCategory(models.Model):
    """
    Model for game categories/genres.
    Provides a more structured way to categorize games.
    """
    
    name = models.CharField(
        max_length=50,
        unique=True,
        help_text="Category name (e.g., Action, RPG, Strategy)"
    )
    description = models.TextField(
        blank=True,
        help_text="Description of this category"
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        help_text="Icon class or emoji for this category"
    )
    color = models.CharField(
        max_length=7,
        default='#667eea',
        help_text="Hex color code for this category"
    )
    
    # SEO
    slug = models.SlugField(
        max_length=50,
        unique=True,
        help_text="URL-friendly version of the name"
    )
    
    # Status
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this category is active"
    )
    
    # Audit Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'game_categories'
        ordering = ['name']
        verbose_name_plural = 'Game Categories'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Override save to auto-generate slug if not provided"""
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
