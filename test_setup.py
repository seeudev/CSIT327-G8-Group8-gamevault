#!/usr/bin/env python3
"""
Test script to verify Django setup for Railway deployment
"""

import sys
import os
from pathlib import Path

# Add the gamevault_backend directory to Python path
BASE_DIR = Path(__file__).resolve().parent
DJANGO_PROJECT_DIR = BASE_DIR / 'gamevault_backend'
sys.path.insert(0, str(DJANGO_PROJECT_DIR))

print(f"Base directory: {BASE_DIR}")
print(f"Django project directory: {DJANGO_PROJECT_DIR}")
print(f"Python path: {sys.path[:3]}")

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamevault_backend.settings')

try:
    import django
    print(f"Django version: {django.get_version()}")
    
    django.setup()
    print("Django setup successful!")
    
    # Test importing apps
    from users import models as user_models
    from store import models as store_models
    print("App imports successful!")
    
except ImportError as e:
    print(f"Import error: {e}")
except Exception as e:
    print(f"Error: {e}")