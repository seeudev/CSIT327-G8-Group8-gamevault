"""
WSGI entry point for Railway deployment.
This file ensures proper module importing for nested Django project structure.
"""

import os
import sys
from pathlib import Path

# Add the gamevault_backend directory to Python path
BASE_DIR = Path(__file__).resolve().parent
DJANGO_PROJECT_DIR = BASE_DIR / 'gamevault_backend'
sys.path.insert(0, str(DJANGO_PROJECT_DIR))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamevault_backend.settings')

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()