#!/usr/bin/env python3
"""
Debug script to test Railway deployment setup
"""

import os
import sys
from pathlib import Path

print("=== Railway Deployment Debug ===")
print(f"Python version: {sys.version}")
print(f"Current working directory: {os.getcwd()}")
print(f"Current file: {__file__}")

# Simulate Railway wsgi.py setup
BASE_DIR = Path(__file__).resolve().parent
DJANGO_PROJECT_DIR = BASE_DIR / 'gamevault_backend'

print(f"Base directory: {BASE_DIR}")
print(f"Django project directory: {DJANGO_PROJECT_DIR}")
print(f"Django project exists: {DJANGO_PROJECT_DIR.exists()}")

# Show what would happen in wsgi.py
print(f"Would change to: {DJANGO_PROJECT_DIR}")
print(f"Would add to sys.path: {DJANGO_PROJECT_DIR}")
print(f"Would set DJANGO_SETTINGS_MODULE to: gamevault_backend.settings")

# Check if key files exist
manage_py = DJANGO_PROJECT_DIR / 'manage.py'
settings_py = DJANGO_PROJECT_DIR / 'gamevault_backend' / 'settings.py'
wsgi_py = DJANGO_PROJECT_DIR / 'gamevault_backend' / 'wsgi.py'

print(f"manage.py exists: {manage_py.exists()}")
print(f"settings.py exists: {settings_py.exists()}")
print(f"wsgi.py exists: {wsgi_py.exists()}")

# Test the path changes
old_cwd = os.getcwd()
old_path = sys.path.copy()

try:
    os.chdir(str(DJANGO_PROJECT_DIR))
    sys.path.insert(0, str(DJANGO_PROJECT_DIR))
    
    print(f"After changes - CWD: {os.getcwd()}")
    print(f"After changes - First sys.path entry: {sys.path[0]}")
    
    # Try to find the settings module
    try:
        import importlib.util
        spec = importlib.util.find_spec('gamevault_backend.settings')
        if spec:
            print(f"✅ Can find gamevault_backend.settings at: {spec.origin}")
        else:
            print("❌ Cannot find gamevault_backend.settings")
    except Exception as e:
        print(f"❌ Error finding settings: {e}")
        
finally:
    # Restore original state
    os.chdir(old_cwd)
    sys.path[:] = old_path