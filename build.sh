#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Navigate to Django project directory
cd gamevault_backend

# Collect static files (--clear removes old files, --no-input runs without prompts)
echo "==================== COLLECTING STATIC FILES ===================="
python manage.py collectstatic --no-input --clear

# Verify static files were collected
echo "==================== VERIFYING STATIC FILES ===================="
echo "Contents of staticfiles directory:"
ls -la staticfiles/ || echo "staticfiles/ directory does not exist!"
echo "Checking for CSS files:"
ls -la staticfiles/css/ || echo "staticfiles/css/ directory does not exist!"
echo "================================================================"

# Run migrations
python manage.py migrate

# Create admin user if it doesn't exist (only for SQLite/first deploy)
python create_admin.py || true