#!/usr/bin/env python3
"""
Verification script for Railway Django deployment
This can be used as a health check or to diagnose issues
"""

import os
import sys
from pathlib import Path

def main():
    print("=== Railway Django Deployment Check ===")
    print(f"Python: {sys.version}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Script location: {__file__}")
    
    # Check if we're in the right place
    cwd = Path.cwd()
    print(f"\nChecking directory structure from: {cwd}")
    
    # Look for key files
    files_to_check = [
        'Procfile',
        'requirements.txt', 
        'wsgi.py',
        'gamevault_backend/manage.py',
        'gamevault_backend/gamevault_backend/settings.py',
        'gamevault_backend/gamevault_backend/wsgi.py'
    ]
    
    for file_path in files_to_check:
        full_path = cwd / file_path
        exists = full_path.exists()
        print(f"  {file_path}: {'✅' if exists else '❌'}")
    
    # Check Django can be imported
    try:
        import django
        print(f"\n✅ Django {django.get_version()} available")
    except ImportError as e:
        print(f"\n❌ Django not available: {e}")
        return False
    
    # Test if we can change to gamevault_backend and import settings
    try:
        django_dir = cwd / 'gamevault_backend'
        if django_dir.exists():
            os.chdir(str(django_dir))
            print(f"✅ Changed to Django directory: {os.getcwd()}")
            
            # Try to import Django settings
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamevault_backend.settings')
            
            import importlib.util
            spec = importlib.util.find_spec('gamevault_backend.settings')
            if spec:
                print(f"✅ Found Django settings at: {spec.origin}")
                
                # Try to actually import and check
                from django.conf import settings
                print(f"✅ Django settings loaded successfully")
                print(f"   DEBUG: {settings.DEBUG}")
                print(f"   INSTALLED_APPS: {len(settings.INSTALLED_APPS)} apps")
                return True
            else:
                print("❌ Cannot find gamevault_backend.settings")
                return False
        else:
            print("❌ gamevault_backend directory not found")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Django setup: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)