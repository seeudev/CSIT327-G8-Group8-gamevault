from django.db import models
from django.conf import settings

class Game(models.Model):
    PLATFORM_CHOICES = [
        ('PC', 'PC'),
        ('PS5', 'PlayStation 5'),
        ('PS4', 'PlayStation 4'),
        ('XBOX', 'Xbox'),
        ('SWITCH', 'Nintendo Switch'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    genre = models.CharField(max_length=100)
    publisher = models.CharField(max_length=200)
    release_date = models.DateField()
    cover_image_url = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    stock_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.platform})"

class GameKey(models.Model):
    STATUS_CHOICES = [
        ('AVAILABLE', 'Available'),
        ('SOLD', 'Sold'),
        ('RESERVED', 'Reserved'),
    ]
    
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='keys')
    key_code = models.CharField(max_length=500, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='AVAILABLE')
    created_at = models.DateTimeField(auto_now_add=True)
    sold_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Key for {self.game.title} - {self.status}"

class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
        ('REFUNDED', 'Refunded'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    game_key = models.ForeignKey(GameKey, on_delete=models.SET_NULL, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.game.title} in Order #{self.order.id}"
