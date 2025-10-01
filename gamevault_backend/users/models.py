from django.contrib.auth.models import AbstractUser
from django.db import models


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
