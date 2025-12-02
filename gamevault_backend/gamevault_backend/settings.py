"""
Django settings for gamevault_backend project.
Simple configuration for GameVault store application.
"""

from pathlib import Path
import os
import dj_database_url
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-zf4(x91kp(kqul1zos2smnu%y)s@bh9w5jk&s%2u*smvjy%zvy')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',') if os.getenv('ALLOWED_HOSTS') else ['*']

# CSRF Trusted Origins
CSRF_TRUSTED_ORIGINS = [
    'https://csit327-g8-group8-gamevault-production.up.railway.app',
    'https://*.railway.app',
    'https://*.onrender.com',
]


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    'users',
    'store'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'store.middleware.CloseDBConnectionMiddleware',  # MUST be last - closes DB connections after all processing
]

ROOT_URLCONF = 'gamevault_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'gamevault_backend' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'store.context_processors.cart_count',
            ],
        },
    },
]

WSGI_APPLICATION = 'gamevault_backend.wsgi.application'


# Database configuration
# For Supabase PostgreSQL, set DATABASE_URL in your .env file
# Example: DATABASE_URL=postgresql://user:password@host:port/database

DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///db.sqlite3',  # Fallback to SQLite for development
        conn_max_age=0,  # Don't persist connections (critical for Supabase Session Pooler)
        conn_health_checks=False,  # Disabled - health checks keep connections alive
    )
}

# Additional Supabase-specific database configuration
# Prevents connection pool exhaustion on free tier Session Pooler
if 'ENGINE' in DATABASES['default'] and 'postgresql' in DATABASES['default']['ENGINE']:
    DATABASES['default']['ATOMIC_REQUESTS'] = False  # Don't wrap requests in transactions
    DATABASES['default']['OPTIONS'] = {
        'connect_timeout': 10,  # Timeout if can't connect within 10 seconds
        'options': '-c statement_timeout=30000',  # Kill queries after 30 seconds
    }


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = '/static/'

# Static files configuration for production
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Static files directories for collectstatic
STATICFILES_DIRS = [
    BASE_DIR / 'gamevault_backend' / 'static',
]

# WhiteNoise Configuration - optimized for production
# Use CompressedStaticFilesStorage (without manifest) for more forgiving behavior
# This won't crash if a static file is missing, it will just return the original path
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

# WhiteNoise settings - allow serving from source directories if STATIC_ROOT doesn't exist
WHITENOISE_USE_FINDERS = True if not os.path.exists(os.path.join(BASE_DIR, 'staticfiles')) else False
WHITENOISE_AUTOREFRESH = False  # Disable autorefresh for production
WHITENOISE_ALLOW_ALL_ORIGINS = True  # Allow CORS for static files
WHITENOISE_MAX_AGE = 31536000  # Cache static files for 1 year

# Create staticfiles directory if it doesn't exist (prevents warning)
os.makedirs(STATIC_ROOT, exist_ok=True)

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'users.User'

# Session configuration (for simple session-based authentication)
SESSION_COOKIE_AGE = 1209600  # 2 weeks in seconds
SESSION_SAVE_EVERY_REQUEST = True

# Login URL
LOGIN_URL = '/auth/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Media files configuration (for game screenshots and user uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Email Configuration (Module 5: Secure Game Delivery)
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@gamevault.com')


# Site URL for email templates
SITE_URL = os.getenv('SITE_URL', 'http://localhost:8000')

# Logging configuration for production debugging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO' if not DEBUG else 'DEBUG',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',  # Log all request errors
            'propagate': False,
        },
    },
}
