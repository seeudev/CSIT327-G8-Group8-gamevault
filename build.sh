#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Navigate to Django project directory
cd gamevault_backend

# Collect static files (--clear removes old files, --no-input runs without prompts)
python manage.py collectstatic --no-input --clear

# Run migrations
python manage.py migrate

# Create admin user if it doesn't exist (only for SQLite/first deploy)
python create_admin.py || true