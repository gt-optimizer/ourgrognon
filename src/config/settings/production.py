from .base import *

DEBUG = False

ALLOWED_HOSTS = [os.environ['ALLOWED_HOSTS']]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ['DB_NAME'],
        'USER': os.environ['DB_USER'],
        'PASSWORD': os.environ['DB_PASSWORD'],
        'HOST': 'postgresql-oursgrognon.alwaysdata.net',
        'PORT': '5432',
    }
}

# Sécurité HTTPS
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True