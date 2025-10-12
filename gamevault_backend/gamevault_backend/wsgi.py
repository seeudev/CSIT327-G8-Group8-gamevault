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

# Set the Django settings module - Railway environment variable should be:
# DJANGO_SETTINGS_MODULE=gamevault_backend.settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamevault_backend.settings')

application = get_wsgi_application()
