import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'horilla.settings')
django.setup()

from django.db import connection

def reset_database():
    """Drop and recreate the public schema"""
    with connection.cursor() as cursor:
        print("Dropping public schema...")
        cursor.execute("DROP SCHEMA public CASCADE;")
        
        print("Creating public schema...")
        cursor.execute("CREATE SCHEMA public;")
        
        print("SUCCESS: Database reset complete! Public schema has been recreated.")
        print("\nNext steps:")
        print("1. Run: python manage.py migrate")
        print("2. Run: python manage.py createsuperuser")

if __name__ == "__main__":
    try:
        reset_database()
    except Exception as e:
        print(f"ERROR: {e}")
        print("\nMake sure your DATABASE_URL is correctly configured.")

