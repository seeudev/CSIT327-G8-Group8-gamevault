from django.db import models
from django.contrib.auth import get_user_model
from decimal import Decimal
import uuid

User = get_user_model()


class Game(models.Model):
    """
    Simple Game model for storing game information in the store.
    """
    # game_id is the primary key (id field by default)
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    screenshot_url = models.URLField(blank=True, null=True)
    file_url = models.URLField(blank=True, null=True)  # URL to download the game file
    upload_date = models.DateTimeField(auto_now_add=True)

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

    class Meta:
        db_table = 'transaction_items'

    def __str__(self):
        return f"{self.game.title} in Transaction {self.transaction.id}"


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
