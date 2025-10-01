from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    """
    Management command to drop all tables in the database.
    WARNING: This should only be used in development!
    """
    help = 'Drop all tables in the database (DEVELOPMENT ONLY)'

    def handle(self, *args, **options):
        """Execute the table drop"""
        self.stdout.write(
            self.style.WARNING('WARNING: This will delete ALL tables and data!')
        )
        
        with connection.cursor() as cursor:
            # Get all table names
            cursor.execute("""
                SELECT tablename FROM pg_tables
                WHERE schemaname = 'public';
            """)
            tables = cursor.fetchall()
            
            if not tables:
                self.stdout.write(
                    self.style.WARNING('No tables found in the database.')
                )
                return
            
            # Drop all tables
            for table in tables:
                table_name = table[0]
                self.stdout.write(f'Dropping table: {table_name}')
                cursor.execute(f'DROP TABLE IF EXISTS "{table_name}" CASCADE;')
            
        self.stdout.write(
            self.style.SUCCESS('All tables dropped successfully!')
        )
        self.stdout.write(
            self.style.SUCCESS('Run "python manage.py migrate" to create fresh tables.')
        )
