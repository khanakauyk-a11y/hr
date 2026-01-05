"""
Django settings for hr_portal project.

This repo is intended to be deployed (e.g., on Hostinger VPS) so we read the
important settings from environment variables when available.
"""

import os
from pathlib import Path

import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-xd$be1p_svb0wbs()utw=v_a@i)cna-f#cncak@_w0kbi_d)px",
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"

# Comma-separated list: "example.com,www.example.com"
ALLOWED_HOSTS = [
    h.strip()
    for h in os.environ.get("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost,.railway.app").split(",")
    if h.strip()
]

# Behind Nginx/HTTPS on a VPS, Django should respect forwarded proto/host
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

# Comma-separated list with scheme, e.g. "https://example.com,https://www.example.com"
CSRF_TRUSTED_ORIGINS = [
    o.strip()
    for o in os.environ.get("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",")
    if o.strip()
]

# Railway convenience: if the public domain env var exists, trust it automatically.
_railway_domain = os.environ.get("RAILWAY_PUBLIC_DOMAIN", "").strip()
if _railway_domain:
    CSRF_TRUSTED_ORIGINS.append(f"https://{_railway_domain}")


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'org',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'hr_portal.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'hr_portal.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

_default_db_url = f"sqlite:///{(BASE_DIR / 'db.sqlite3').as_posix()}"

# Railway typically provides either DATABASE_URL or PG* vars (via the Postgres service).
_pg_host = os.environ.get("PGHOST", "").strip()
_pg_db = os.environ.get("PGDATABASE", "").strip()
_pg_user = os.environ.get("PGUSER", "").strip()
_pg_pass = os.environ.get("PGPASSWORD", "").strip()
_pg_port = os.environ.get("PGPORT", "").strip()
if _pg_host and _pg_db and _pg_user and _pg_port:
    _default_db_url = f"postgresql://{_pg_user}:{_pg_pass}@{_pg_host}:{_pg_port}/{_pg_db}"

DATABASES = {
    "default": dj_database_url.config(
        default=os.environ.get("DATABASE_URL", _default_db_url),
        conn_max_age=int(os.environ.get("DJANGO_DB_CONN_MAX_AGE", "600")),
    )
}

_sslmode = os.environ.get("DJANGO_DB_SSLMODE", "").strip()
if _sslmode:
    DATABASES["default"].setdefault("OPTIONS", {})
    DATABASES["default"]["OPTIONS"]["sslmode"] = _sslmode


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
    },
}

# Media files (User uploads - offer letters, etc.)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Auth redirects
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "dashboard"
LOGOUT_REDIRECT_URL = "home"

# HR portal defaults
HR_DEFAULT_PASSWORD = os.environ.get("HR_DEFAULT_PASSWORD", "Welcome@123")

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
