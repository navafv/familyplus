from .base import *
import dj_database_url
import os
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

# Initialize Sentry
SENTRY_DSN = config('SENTRY_DSN', default=None)
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        traces_sample_rate=1.0,
        send_default_pii=True
    )

DEBUG = False

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='navaf.pythonanywhere.com,www.navaf.pythonanywhere.com', cast=lambda v: [s.strip() for s in v.split(',')])

# Database Configuration pull from environment variable (DATABASE_URL)
# Falls back to individual config vars if DATABASE_URL is not found
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL', default=''),
        conn_max_age=600,
        ssl_require=True if config('DATABASE_URL', default='') else False
    )
}

# Ensure fallback for environments where DATABASE_URL is not used
if not DATABASES['default']:
    DATABASES['default'] = {
        'ENGINE': config('DATABASE_ENGINE'),
        'NAME': config('DATABASE_NAME'),
        'USER': config('DATABASE_USER'),
        'PASSWORD': config('DATABASE_PASSWORD'),
        'HOST': config('DATABASE_HOST'),
        'PORT': config('DATABASE_PORT'),
        'CONN_MAX_AGE': 600,
    }

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Security & HTTPS
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = 'same-origin'
X_FRAME_OPTIONS = 'DENY'

CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', default='', cast=lambda v: [s.strip() for s in v.split(',')])

# CORS Production Settings
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='', cast=lambda v: [s.strip() for s in v.split(',')])

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '[{asctime}] {levelname} {name}: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {'class': 'logging.StreamHandler', 'formatter': 'default'},
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'familyplus.log',
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'formatter': 'default',
        },
    },
    'loggers': {
        'django': {'handlers': ['console', 'file'], 'level': 'INFO'},
    },
}

os.makedirs(BASE_DIR / 'logs', exist_ok=True)
