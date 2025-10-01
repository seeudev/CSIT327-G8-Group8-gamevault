"""
Script to reset the Supabase database and apply fresh migrations.
This will drop all existing tables and recreate them with the new schema.
"""

import os
import django
import psycopg2
from urllib.parse import urlparse

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamevault_backend.settings')
django.setup()

from django.conf import settings

# Parse the DATABASE_URL
db_url = settings.DATABASES['default']
db_config = {
    'dbname': db_url['NAME'],
    'user': db_url['USER'],
    'password': db_url['PASSWORD'],
    'host': db_url['HOST'],
    'port': db_url['PORT'],
}

print("Connecting to Supabase PostgreSQL...")
print(f"Host: {db_config['host']}")
print(f"Database: {db_config['dbname']}")

try:
    # Connect to database
    conn = psycopg2.connect(**db_config)
    conn.autocommit = True
    cursor = conn.cursor()
    
    print("\nChecking existing tables...")
    cursor.execute("""
        SELECT tablename FROM pg_tables 
        WHERE schemaname = 'public' 
        ORDER BY tablename;
    """)
    tables = cursor.fetchall()
    
    if tables:
        print(f"Found {len(tables)} tables:")
        for table in tables:
            print(f"  - {table[0]}")
        
        response = input("\nDo you want to drop all tables and start fresh? (yes/no): ")
        if response.lower() == 'yes':
            print("\nDropping all tables...")
            
            # Drop all tables in public schema
            cursor.execute("""
                DO $$ DECLARE
                    r RECORD;
                BEGIN
                    FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
                        EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
                    END LOOP;
                END $$;
            """)
            
            print("All tables dropped successfully!")
            print("\nNow run: python manage.py migrate")
        else:
            print("Cancelled. No changes made.")
    else:
        print("No tables found. Database is clean.")
        print("Run: python manage.py migrate")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
    print("\nMake sure your DATABASE_URL is correct in the .env file.")
