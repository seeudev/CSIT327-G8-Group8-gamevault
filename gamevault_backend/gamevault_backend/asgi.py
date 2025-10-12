"""
ASGI config for gamevault_backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
import sys
from pathlib import Path
from django.core.asgi import get_asgi_application

# Ensure project root (where manage.py lives) is on sys.path so top-level apps are importable
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))  # <-- add this

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamevault_backend.settings')

application = get_asgi_application()
