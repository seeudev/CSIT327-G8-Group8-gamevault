"""
WSGI entry point for Railway deployment.
Simple approach that delegates to the existing Django wsgi.py
"""

import os
import sys
from pathlib import Path

# Get the repo root directory
repo_root = Path(__file__).resolve().parent

# Add the repo root to Python path so we can import gamevault_backend as a module
sys.path.insert(0, str(repo_root))

# Change working directory to the Django project
django_project_path = repo_root / 'gamevault_backend'
os.chdir(str(django_project_path))

# Import the application from the existing Django wsgi.py
# This avoids duplicating configuration and uses Django's standard setup
from gamevault_backend.gamevault_backend.wsgi import application