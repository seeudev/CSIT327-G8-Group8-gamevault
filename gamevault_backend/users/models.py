from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import secrets
from datetime import timedelta


class User(AbstractUser):
    """
    Simple User model for GameVault.
    Stores basic user information for authentication and admin access.
    """
    # user_id is inherited as 'id' from AbstractUser (Primary Key)
    # username is inherited from AbstractUser
    # password is stored as password_hash via AbstractUser's password field
    
    email = models.EmailField(unique=True)
    registration_date = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)

    class Meta:
        db_table = 'users'
        ordering = ['-registration_date']

    def __str__(self):
        return self.username


class PasswordResetToken(models.Model):
    """
    Password reset token model for secure password recovery.
    Tokens expire after 1 hour and can only be used once.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_reset_tokens')
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    class Meta:
        db_table = 'password_reset_tokens'
        ordering = ['-created_at']

    def __str__(self):
        return f"Reset token for {self.user.username} - {self.token[:8]}..."

    def save(self, *args, **kwargs):
        """Auto-generate token and expiration time on creation"""
        if not self.token:
            self.token = secrets.token_urlsafe(32)
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=1)
        super().save(*args, **kwargs)

    def is_valid(self):
        """Check if token is still valid (not expired and not used)"""
        return not self.is_used and timezone.now() < self.expires_at

    @classmethod
    def create_token(cls, user):
        """Create a new password reset token for a user"""
        # Invalidate all existing tokens for this user
        cls.objects.filter(user=user, is_used=False).update(is_used=True)
        # Create new token
        return cls.objects.create(user=user)
