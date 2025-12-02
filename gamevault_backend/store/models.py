from django.db import models
from django.contrib.auth import get_user_model
from decimal import Decimal
import uuid
import secrets

User = get_user_model()

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist_items')
    game = models.ForeignKey('Game', on_delete=models.CASCADE, related_name='wishlisted_by')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'game')
        verbose_name = 'Wishlist Item'
        verbose_name_plural = 'Wislist Items'

    def __str__(self):
        return f"{self.user} - {self.game}"


class Category(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'tags'
        ordering = ['name']

    def __str__(self):
        return self.name


class GameTag(models.Model):
    game = models.ForeignKey('Game', on_delete=models.CASCADE)
    tag = models.ForeignKey('Tag', on_delete=models.CASCADE)

    class Meta:
        db_table = 'game_tags'
        unique_together = ('game', 'tag')

    def __str__(self):
        return f"{self.game.title} - {self.tag.name}"


class Game(models.Model):
    """
    Simple Game model for storing game information in the store.
    Module 17: AI Hybrid Market Analysis fields added.
    """
    # game_id is the primary key (id field by default)
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    screenshot_url = models.URLField(blank=True, null=True)
    file_url = models.URLField(blank=True, null=True)  # URL to download the game file
    upload_date = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField(Tag, through='GameTag', related_name='games')
    
    # Module 17: AI Hybrid Market Analysis
    external_sources = models.JSONField(default=list, blank=True, null=True, help_text="Citation metadata: [{source_name, url, sentiment}]")
    global_sentiment_score = models.FloatField(null=True, blank=True, help_text="Web sentiment score (0-100)")
    local_rating = models.FloatField(null=True, blank=True, help_text="Local buyer rating (0-5 stars converted to 0-100)")
    ai_verdict = models.TextField(blank=True, null=True, help_text="AI-generated consensus summary")
    last_external_sync = models.DateTimeField(null=True, blank=True, help_text="Last time external data was fetched")
    last_local_sync = models.DateTimeField(null=True, blank=True, help_text="Last time local reviews were analyzed")
    game_exists_externally = models.BooleanField(default=True, help_text="Whether game exists in external sources")

    class Meta:
        db_table = 'games'
        ordering = ['-upload_date']

    def __str__(self):
        return self.title


class Cart(models.Model):
    """
    Shopping cart model for users.
    """
    # cart_id is the primary key (id field by default)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carts')
    created_at = models.DateTimeField(auto_now_add=True)
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('checked_out', 'Checked Out'),
        ('abandoned', 'Abandoned'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    class Meta:
        db_table = 'carts'
        ordering = ['-created_at']

    def __str__(self):
        return f"Cart {self.id} - {self.user.username}"

    def get_total(self):
        """Calculate total price of all items in cart"""
        total = Decimal('0.00')
        for item in self.items.all():
            total += item.price_at_addition * item.quantity
        return total


class CartItem(models.Model):
    """
    Individual items in a shopping cart.
    """
    # cart_item_id is the primary key (id field by default)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price_at_addition = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'cart_items'
        # Ensure a game appears only once per cart
        unique_together = ['cart', 'game']

    def __str__(self):
        return f"{self.game.title} x{self.quantity} in Cart {self.cart.id}"

    def get_subtotal(self):
        """Calculate subtotal for this item"""
        return self.price_at_addition * self.quantity


class Transaction(models.Model):
    """
    Transaction model for completed purchases.
    """
    # transaction_id is the primary key (id field by default)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    transaction_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='completed')
    download_token = models.UUIDField(default=uuid.uuid4, unique=True)

    class Meta:
        db_table = 'transactions'
        ordering = ['-transaction_date']

    def __str__(self):
        return f"Transaction {self.id} - {self.user.username} - ${self.total_amount}"


class TransactionItem(models.Model):
    """
    Individual items in a transaction.
    """
    # transaction_item_id is the primary key (id field by default)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='items')
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)
    game_key = models.CharField(max_length=50, unique=True, blank=True, null=True)
    key_sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'transaction_items'

    def __str__(self):
        return f"{self.game.title} in Transaction {self.transaction.id}"
    
    def generate_game_key(self):
        """Generate a unique game key for this purchase."""
        if not self.game_key:
            # Generate format: GAME-XXXX-XXXX-XXXX
            key_parts = [
                'GAME',
                secrets.token_hex(2).upper(),
                secrets.token_hex(2).upper(),
                secrets.token_hex(2).upper()
            ]
            self.game_key = '-'.join(key_parts)
            self.save()
        return self.game_key


class AdminActionLog(models.Model):
    """
    Log model for tracking admin actions on games.
    """
    # log_id is the primary key (id field by default)
    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='admin_actions')
    
    ACTION_TYPE_CHOICES = [
        ('create', 'Create Game'),
        ('update', 'Update Game'),
        ('delete', 'Delete Game'),
    ]
    action_type = models.CharField(max_length=20, choices=ACTION_TYPE_CHOICES)
    target_game = models.ForeignKey(Game, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'admin_action_logs'
        ordering = ['-timestamp']

    def __str__(self):
        admin_name = self.admin.username if self.admin else 'Unknown'
        game_title = self.target_game.title if self.target_game else 'N/A'
        return f"{admin_name} - {self.action_type} - {game_title}"


class EmailLog(models.Model):
    """
    Log model for tracking sent game key emails.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_logs')
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    game_key = models.CharField(max_length=50)
    sent_at = models.DateTimeField(auto_now_add=True)
    email_to = models.EmailField()
    
    STATUS_CHOICES = [
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    
    class Meta:
        db_table = 'email_logs'
        ordering = ['-sent_at']

    def __str__(self):
        return f"Email to {self.user.username} for {self.game.title} - {self.status}"


class Review(models.Model):
    """
    Review model for game ratings and reviews (Module 11).
    Users can rate and review games they own.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(
        choices=[(1, '1 Star'), (2, '2 Stars'), (3, '3 Stars'), (4, '4 Stars'), (5, '5 Stars')],
        help_text='Rating from 1 to 5 stars'
    )
    review_text = models.TextField(blank=True, help_text='Optional review text')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'reviews'
        ordering = ['-created_at']  # Most recent first
        # One review per user per game
        unique_together = ['user', 'game']
        indexes = [
            models.Index(fields=['game', '-created_at']),  # For fetching game reviews
            models.Index(fields=['user', '-created_at']),  # For fetching user reviews
        ]

    def __str__(self):
        return f"{self.user.username}'s review of {self.game.title} - {self.rating} stars"

    @staticmethod
    def get_average_rating(game):
        """Calculate average rating for a game."""
        from django.db.models import Avg
        result = Review.objects.filter(game=game).aggregate(avg_rating=Avg('rating'))
        avg = result['avg_rating']
        return round(avg, 1) if avg else None

    @staticmethod
    def get_rating_stats(game):
        """Get detailed rating statistics for a game."""
        from django.db.models import Count, Avg
        stats = Review.objects.filter(game=game).aggregate(
            avg_rating=Avg('rating'),
            total_reviews=Count('id'),
            five_star=Count('id', filter=models.Q(rating=5)),
            four_star=Count('id', filter=models.Q(rating=4)),
            three_star=Count('id', filter=models.Q(rating=3)),
            two_star=Count('id', filter=models.Q(rating=2)),
            one_star=Count('id', filter=models.Q(rating=1)),
        )
        if stats['avg_rating']:
            stats['avg_rating'] = round(stats['avg_rating'], 1)
        return stats


class Promotion(models.Model):
    """
    Promotion model for managing discounts on games and categories (Module 16).
    Supports both percentage and fixed amount discounts.
    """
    name = models.CharField(max_length=200, help_text='Promotion name for admin reference')
    description = models.TextField(blank=True, help_text='Promotion description')
    
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Percentage Discount'),
        ('fixed', 'Fixed Amount Discount'),
    ]
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES, default='percentage')
    discount_value = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text='Percentage (0-100) or fixed amount'
    )
    
    # Promotion can apply to specific games or entire categories
    games = models.ManyToManyField(Game, blank=True, related_name='promotions')
    categories = models.ManyToManyField(Category, blank=True, related_name='promotions')
    
    # Date range for automatic activation/deactivation
    start_date = models.DateTimeField(help_text='Promotion start date and time')
    end_date = models.DateTimeField(help_text='Promotion end date and time')
    
    # Manual override
    is_active = models.BooleanField(default=True, help_text='Manually activate/deactivate promotion')
    
    # Tracking
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_promotions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'promotions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['start_date', 'end_date', 'is_active']),  # For active promotion queries
        ]

    def __str__(self):
        discount_display = f"{self.discount_value}%" if self.discount_type == 'percentage' else f"${self.discount_value}"
        return f"{self.name} - {discount_display}"

    def is_currently_active(self):
        """Check if promotion is currently active based on dates and manual override."""
        from django.utils import timezone
        now = timezone.now()
        return (
            self.is_active and 
            self.start_date <= now <= self.end_date
        )

    def calculate_discounted_price(self, original_price):
        """Calculate discounted price for a given original price."""
        if not self.is_currently_active():
            return original_price
        
        if self.discount_type == 'percentage':
            discount_amount = original_price * (self.discount_value / Decimal('100'))
            discounted_price = original_price - discount_amount
        else:  # fixed
            discounted_price = original_price - self.discount_value
        
        # Ensure price doesn't go below 0
        return max(discounted_price, Decimal('0.00'))

    def get_applicable_games(self):
        """Get all games this promotion applies to (including category games)."""
        from django.db.models import Q
        game_ids = set(self.games.values_list('id', flat=True))
        
        # Add games from categories
        for category in self.categories.all():
            category_game_ids = Game.objects.filter(category=category).values_list('id', flat=True)
            game_ids.update(category_game_ids)
        
        return Game.objects.filter(id__in=game_ids)


class PromotionUsage(models.Model):
    """
    Track promotion usage for sales reporting (Module 16).
    Records each time a promotion is applied to a purchase.
    """
    promotion = models.ForeignKey(Promotion, on_delete=models.CASCADE, related_name='usages')
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='promotions_used')
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    original_price = models.DecimalField(max_digits=10, decimal_places=2)
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    used_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'promotion_usages'
        ordering = ['-used_at']
        indexes = [
            models.Index(fields=['promotion', '-used_at']),  # For promotion reports
            models.Index(fields=['transaction']),  # For transaction lookups
        ]

    def __str__(self):
        return f"{self.promotion.name} applied to {self.game.title} - Saved ${self.discount_amount}"
