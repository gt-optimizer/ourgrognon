from .base import *
import os

DEBUG = False

ALLOWED_HOSTS = [os.environ['ALLOWED_HOSTS']]

CSRF_TRUSTED_ORIGINS = [
    'https://oursgrognon.alwaysdata.net',
    'https://oursgrognon.optimizer-labs.fr',
]

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

STATIC_ROOT = '/home/oursgrognon/www/src/staticfiles'
MEDIA_ROOT = '/home/oursgrognon/www/src/media'


SECURE_SSL_REDIRECT = False
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')