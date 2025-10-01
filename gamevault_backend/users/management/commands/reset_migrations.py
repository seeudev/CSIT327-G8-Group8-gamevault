from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    """
    Management command to reset migration history.
    WARNING: This should only be used in development!
    """
    help = 'Reset migration history in the database'

    def handle(self, *args, **options):
        """Execute the migration reset"""
        self.stdout.write(
            self.style.WARNING('WARNING: This will delete all migration records!')
        )
        
        with connection.cursor() as cursor:
            # Delete all migration records
            cursor.execute("DELETE FROM django_migrations;")
            
        self.stdout.write(
            self.style.SUCCESS('All migration records deleted successfully!')
        )
        self.stdout.write(
            self.style.SUCCESS('Run "python manage.py migrate --fake-initial" to re-apply migrations.')
        )
