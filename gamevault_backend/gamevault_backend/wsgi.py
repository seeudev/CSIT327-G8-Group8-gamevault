"""
WSGI config for gamevault_backend project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import sys
from pathlib import Path
from django.core.wsgi import get_wsgi_application

# When using gunicorn --chdir, we need to add the working directory to Python path
# This allows Django to find the settings module at gamevault_backend.settings
BASE_DIR = Path(__file__).resolve().parent.parent
working_dir = Path.cwd()

# Add the current working directory (where manage.py is) to sys.path
# This should be /app/gamevault_backend when using --chdir
sys.path.insert(0, str(working_dir))

# Debug logging for Railway
print(f"WSGI DEBUG: BASE_DIR = {BASE_DIR}")
print(f"WSGI DEBUG: Working directory = {working_dir}")  
print(f"WSGI DEBUG: sys.path[0] = {sys.path[0]}")

# Check what's already in DJANGO_SETTINGS_MODULE
current_settings = os.environ.get('DJANGO_SETTINGS_MODULE')
print(f"WSGI DEBUG: Current DJANGO_SETTINGS_MODULE = {current_settings}")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamevault_backend.settings')

# Verify what it's set to now
final_settings = os.environ.get('DJANGO_SETTINGS_MODULE')
print(f"WSGI DEBUG: Final DJANGO_SETTINGS_MODULE = {final_settings}")

# Test if we can find the settings module
try:
    import importlib.util
    spec = importlib.util.find_spec('gamevault_backend.settings')
    print(f"WSGI DEBUG: Can find gamevault_backend.settings = {spec is not None}")
    if spec:
        print(f"WSGI DEBUG: Settings location = {spec.origin}")
    else:
        # Try to see what's in the gamevault_backend directory
        import os
        items = os.listdir('gamevault_backend')
        print(f"WSGI DEBUG: gamevault_backend directory contains: {items}")
except Exception as e:
    print(f"WSGI DEBUG: Error during import test: {e}")

application = get_wsgi_application()
