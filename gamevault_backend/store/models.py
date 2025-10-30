from django.db import models
from django.contrib.auth import get_user_model
from decimal import Decimal
import uuid
import secrets

User = get_user_model()

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
