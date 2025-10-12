"""
WSGI entry point for Railway deployment.
This file ensures proper module importing for nested Django project structure.
"""

import os
import sys
from pathlib import Path

# Change to the Django project directory so imports work correctly
BASE_DIR = Path(__file__).resolve().parent
DJANGO_PROJECT_DIR = BASE_DIR / 'gamevault_backend'

# Change working directory to where manage.py is located
os.chdir(str(DJANGO_PROJECT_DIR))

# Add the Django project directory to Python path
sys.path.insert(0, str(DJANGO_PROJECT_DIR))

# Use the same settings module path as manage.py
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamevault_backend.settings')

# Import and initialize Django
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()