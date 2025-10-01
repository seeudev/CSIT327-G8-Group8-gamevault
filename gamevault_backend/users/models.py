from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator


class Role(models.Model):
    """
    Role model to define user roles in the system.
    This allows for flexible role-based access control.
    """
    name = models.CharField(
        max_length=50, 
        unique=True,
        validators=[RegexValidator(
            regex=r'^[a-z_]+$',
            message='Role name must contain only lowercase letters and underscores'
        )]
    )
    display_name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    permissions = models.JSONField(
        default=dict,
        help_text="JSON object defining permissions for this role"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'roles'
        ordering = ['name']

    def __str__(self):
        return self.display_name


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    Adds role-based access control and additional user fields.
    """
    # Remove the default email field and make it required
    email = models.EmailField(unique=True, blank=False, null=False)
    
    # Role relationship
    role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        help_text="User's role in the system"
    )
    
    # Additional user fields
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
        )]
    )
    
    date_of_birth = models.DateField(blank=True, null=True)
    
    # Profile information
    bio = models.TextField(max_length=500, blank=True)
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        help_text="User profile picture"
    )
    
    # Account status
    is_verified = models.BooleanField(
        default=False,
        help_text="Whether the user's email has been verified"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)

    class Meta:
        db_table = 'users'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.username} ({self.email})"

    @property
    def is_admin(self):
        """Check if user has admin role"""
        return self.role and self.role.name == 'admin'

    @property
    def is_buyer(self):
        """Check if user has buyer role"""
        return self.role and self.role.name == 'buyer'

    def get_full_name(self):
        """Return the user's full name"""
        return f"{self.first_name} {self.last_name}".strip() or self.username

    def has_permission(self, permission):
        """Check if user has a specific permission"""
        if not self.role or not self.role.permissions:
            return False
        return self.role.permissions.get(permission, False)
