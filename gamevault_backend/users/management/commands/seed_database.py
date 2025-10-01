from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import Role
import os

User = get_user_model()


class Command(BaseCommand):
    """
    Management command to seed the database with default roles and admin user.
    
    Usage:
    python manage.py seed_database
    """
    help = 'Seed the database with default roles and admin user'

    def add_arguments(self, parser):
        parser.add_argument(
            '--admin-email',
            type=str,
            default='admin@gamevault.com',
            help='Email for the default admin user'
        )
        parser.add_argument(
            '--admin-username',
            type=str,
            default='admin',
            help='Username for the default admin user'
        )
        parser.add_argument(
            '--admin-password',
            type=str,
            default='admin123',
            help='Password for the default admin user'
        )

    def handle(self, *args, **options):
        """Execute the seeding process"""
        self.stdout.write(
            self.style.SUCCESS('Starting database seeding...')
        )

        # Create default roles
        self.create_roles()
        
        # Create default admin user
        self.create_admin_user(
            email=options['admin_email'],
            username=options['admin_username'],
            password=options['admin_password']
        )

        self.stdout.write(
            self.style.SUCCESS('Database seeding completed successfully!')
        )

    def create_roles(self):
        """Create default roles in the system"""
        roles_data = [
            {
                'name': 'admin',
                'display_name': 'Administrator',
                'description': 'Full system access with all permissions',
                'permissions': {
                    'manage_users': True,
                    'manage_games': True,
                    'manage_orders': True,
                    'view_analytics': True,
                    'system_settings': True,
                    'manage_roles': True
                }
            },
            {
                'name': 'buyer',
                'display_name': 'Buyer',
                'description': 'Standard user who can purchase games',
                'permissions': {
                    'view_games': True,
                    'purchase_games': True,
                    'view_own_orders': True,
                    'manage_own_profile': True
                }
            },
            {
                'name': 'moderator',
                'display_name': 'Moderator',
                'description': 'Limited admin access for content moderation',
                'permissions': {
                    'manage_games': True,
                    'view_orders': True,
                    'manage_users': False,
                    'view_analytics': True
                }
            }
        ]

        for role_data in roles_data:
            role, created = Role.objects.get_or_create(
                name=role_data['name'],
                defaults=role_data
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created role: {role.display_name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Role already exists: {role.display_name}')
                )

    def create_admin_user(self, email, username, password):
        """Create default admin user"""
        try:
            # Get admin role
            admin_role = Role.objects.get(name='admin')
            
            # Check if admin user already exists
            if User.objects.filter(username=username).exists():
                self.stdout.write(
                    self.style.WARNING(f'Admin user "{username}" already exists')
                )
                return
            
            if User.objects.filter(email=email).exists():
                self.stdout.write(
                    self.style.WARNING(f'Admin user with email "{email}" already exists')
                )
                return

            # Create admin user
            admin_user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name='System',
                last_name='Administrator',
                role=admin_role,
                is_staff=True,
                is_superuser=True,
                is_active=True,
                is_verified=True
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f'Created admin user: {admin_user.username} ({admin_user.email})'
                )
            )
            self.stdout.write(
                self.style.WARNING(
                    f'Default admin credentials:\n'
                    f'Username: {username}\n'
                    f'Email: {email}\n'
                    f'Password: {password}\n'
                    f'Please change the password after first login!'
                )
            )

        except Role.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('Admin role not found. Please run role creation first.')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating admin user: {str(e)}')
            )
