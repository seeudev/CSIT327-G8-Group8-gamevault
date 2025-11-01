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


class LoginAttempt(models.Model):
    """
    Track failed login attempts for security.
    After 4 failed attempts, user is temporarily locked out for 15 minutes.
    """
    username = models.CharField(max_length=150, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    successful = models.BooleanField(default=False)

    class Meta:
        db_table = 'login_attempts'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['username', '-timestamp']),
        ]

    def __str__(self):
        status = "Success" if self.successful else "Failed"
        return f"{status} login attempt for {self.username} at {self.timestamp}"

    @classmethod
    def record_attempt(cls, username, ip_address=None, successful=False):
        """Record a login attempt"""
        return cls.objects.create(
            username=username,
            ip_address=ip_address,
            successful=successful
        )

    @classmethod
    def get_failed_attempts(cls, username, minutes=15):
        """Get count of failed login attempts for username in last N minutes"""
        cutoff_time = timezone.now() - timedelta(minutes=minutes)
        return cls.objects.filter(
            username=username,
            successful=False,
            timestamp__gte=cutoff_time
        ).count()

    @classmethod
    def is_locked_out(cls, username, max_attempts=4, lockout_minutes=15):
        """
        Check if username is locked out due to too many failed attempts.
        Returns (is_locked, remaining_time_seconds)
        """
        cutoff_time = timezone.now() - timedelta(minutes=lockout_minutes)
        failed_attempts = cls.objects.filter(
            username=username,
            successful=False,
            timestamp__gte=cutoff_time
        ).order_by('-timestamp')

        count = failed_attempts.count()
        
        if count >= max_attempts:
            # User is locked out - calculate remaining time
            latest_attempt = failed_attempts.first()
            lockout_end = latest_attempt.timestamp + timedelta(minutes=lockout_minutes)
            remaining_seconds = (lockout_end - timezone.now()).total_seconds()
            
            if remaining_seconds > 0:
                return True, int(remaining_seconds)
        
        return False, 0

    @classmethod
    def clear_attempts(cls, username):
        """Clear failed login attempts for username (called on successful login)"""
        cls.objects.filter(username=username, successful=False).delete()

    @classmethod
    def cleanup_old_attempts(cls, days=30):
        """Clean up login attempts older than N days"""
        cutoff_time = timezone.now() - timedelta(days=days)
        return cls.objects.filter(timestamp__lt=cutoff_time).delete()
