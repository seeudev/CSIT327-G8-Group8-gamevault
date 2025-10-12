"""
WSGI entry point for Railway deployment.
Contains debugging information for troubleshooting.
"""

import os
import sys
from pathlib import Path

# Debug information - Railway will log this
print("=== WSGI DEBUG INFO ===")
print(f"Python version: {sys.version}")
print(f"Current working directory: {os.getcwd()}")
print(f"__file__: {__file__}")
print(f"sys.path first 3 entries: {sys.path[:3]}")

# This wsgi.py should NOT be used if Procfile uses cd command
# But keeping it as fallback for debugging
repo_root = Path(__file__).resolve().parent
django_project_path = repo_root / 'gamevault_backend'

print(f"Repo root: {repo_root}")
print(f"Django project path: {django_project_path}")
print(f"Django project exists: {django_project_path.exists()}")

if django_project_path.exists():
    print("Directory contents:")
    for item in django_project_path.iterdir():
        print(f"  {item.name}")
    
    wsgi_file = django_project_path / 'gamevault_backend' / 'wsgi.py'
    print(f"Inner wsgi.py exists: {wsgi_file.exists()}")

# Fallback application for debugging
def application(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'text/plain')]
    start_response(status, headers)
    
    debug_info = f"""
Railway Django Deployment Debug Info:

Working Directory: {os.getcwd()}
Python Path: {sys.path}
Environment Variables:
  DJANGO_SETTINGS_MODULE: {os.environ.get('DJANGO_SETTINGS_MODULE', 'Not set')}
  
This is a fallback WSGI application for debugging.
The Procfile should use: cd gamevault_backend && gunicorn gamevault_backend.wsgi:application
"""
    return [debug_info.encode('utf-8')]