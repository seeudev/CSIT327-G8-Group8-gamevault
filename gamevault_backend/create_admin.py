"""
Script to create an admin user for testing.
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamevault_backend.settings')
django.setup()

from users.models import User

# Create admin user if it doesn't exist
if not User.objects.filter(username='admin').exists():
    admin_user = User.objects.create_superuser(
        username='admin',
        email='admin@gamevault.com',
        password='admin123'
    )
    admin_user.is_admin = True
    admin_user.save()
    print('Admin user created successfully!')
    print('Username: admin')
    print('Password: admin123')
else:
    print('Admin user already exists')
