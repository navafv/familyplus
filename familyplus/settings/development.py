from .base import *

DEBUG = True
ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': config('DATABASE_ENGINE', default='django.db.backends.sqlite3'),
        'NAME': config('DATABASE_NAME', default=BASE_DIR / 'db.sqlite3'),
        'USER': config('DATABASE_USER', default=''),
        'PASSWORD': config('DATABASE_PASSWORD', default=''),
        'HOST': config('DATABASE_HOST', default=''),
        'PORT': config('DATABASE_PORT', default=''),
    }
}

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'familyplus' / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Dev-only tools
INSTALLED_APPS += [
    # 'django_extensions',  # optional (shell_plus, etc.)
]

# CORS Development Settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
]
