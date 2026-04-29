import os
from .base import *
import dj_database_url

DEBUG = False
SECRET_KEY = os.environ.get('SECRET_KEY') 

ALLOWED_HOSTS = [
    'binis-invoices.onrender.com', 
    '.onrender.com'
]

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
CSRF_TRUSTED_ORIGINS = ['https://binis-invoices.onrender.com']

DATABASES = {
    'default': dj_database_url.config(
        conn_max_age=600,
        conn_health_checks=True,
    )
}

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'