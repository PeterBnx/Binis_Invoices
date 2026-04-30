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
CORS_ALLOWED_ORIGINS = [
    "https://binis-invoices.vercel.app",
    "https://binis-invoices-9yvum0rin-peter-bnx-s-projects.vercel.app",
]

CORS_ALLOW_HEADERS = [
    "accept",
    "authorization",
    "content-type",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]

CORS_ALLOW_CREDENTIALS = True
SESSION_COOKIE_SAMESITE = 'None'
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = 'None'
CSRF_COOKIE_SECURE = True

CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://binis-invoices-.*\.vercel\.app$",
]

CSRF_TRUSTED_ORIGINS = [
    "https://binis-invoices.vercel.app",
    "https://binis-invoices-7eiimmwpj-peter-bnx-s-projects.vercel.app"
]


DATABASES = {
    'default': dj_database_url.config(
        conn_max_age=600,
        conn_health_checks=True,
    )
}

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'