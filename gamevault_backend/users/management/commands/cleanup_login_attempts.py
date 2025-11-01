"""
Management command to clean up old login attempts.
Usage: python manage.py cleanup_login_attempts [--days 30]
"""

from django.core.management.base import BaseCommand
from users.models import LoginAttempt


class Command(BaseCommand):
    help = 'Clean up login attempts older than specified days (default: 30)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Delete login attempts older than this many days (default: 30)',
        )

    def handle(self, *args, **options):
        days = options['days']
        
        deleted_count, _ = LoginAttempt.cleanup_old_attempts(days=days)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully deleted {deleted_count} login attempt(s) older than {days} days'
            )
        )
