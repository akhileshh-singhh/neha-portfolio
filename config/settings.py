"""
Settings for the Neha Varma portfolio CMS.

Everything environment-specific comes from environment variables, so the same
code runs locally and on Render / Railway / any VPS.  See .env.example.
"""
import os
from pathlib import Path

import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent


def env(name, default=None):
    return os.environ.get(name, default)


def env_bool(name, default=False):
    return str(env(name, "1" if default else "0")).lower() in {"1", "true", "yes", "on"}


def env_list(name, default=""):
    return [x.strip() for x in env(name, default).split(",") if x.strip()]


# Load a local .env file if present (no extra dependency needed).
_env_file = BASE_DIR / ".env"
if _env_file.exists():
    for line in _env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

SECRET_KEY = env("SECRET_KEY", "dev-only-insecure-key-change-me")
DEBUG = env_bool("DEBUG", False)

ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", "localhost,127.0.0.1")
CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS", "")
if env("RENDER_EXTERNAL_HOSTNAME"):  # Render sets this automatically
    ALLOWED_HOSTS.append(env("RENDER_EXTERNAL_HOSTNAME"))
    CSRF_TRUSTED_ORIGINS.append("https://" + env("RENDER_EXTERNAL_HOSTNAME"))

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    'cloudinary_storage',
    "django.contrib.staticfiles",
    'cloudinary',
    "rest_framework",
    "adminsortable2",
    "cms",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],  # project templates win over app templates
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "cms.context_processors.site_globals",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}", conn_max_age=600
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en"
TIME_ZONE = env("TIME_ZONE", "Asia/Kolkata")
USE_I18N = True
USE_TZ = True

# Serve static files straight from the apps (admin, cms) so the site and admin are styled
# even if `collectstatic` has not been run (e.g. plain `runserver` with DEBUG off).
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = DEBUG
X_FRAME_OPTIONS = "SAMEORIGIN"  # lets the dashboard show a live preview of the site

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Modern Django Storage configuration
STORAGES = {
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

# FIX: Provide fallback for packages (like django-cloudinary-storage) looking for legacy settings
STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"

# Uploaded images / videos.  On Render attach a persistent disk and point
# MEDIA_ROOT at it (e.g. /var/data/media) or switch to S3/Cloudinary storage.
MEDIA_URL = "/media/"
MEDIA_ROOT = Path(env("MEDIA_ROOT", str(BASE_DIR / "media")))
SERVE_MEDIA = env_bool("SERVE_MEDIA", True)
DATA_UPLOAD_MAX_MEMORY_SIZE = 25 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_THROTTLE_CLASSES": ["rest_framework.throttling.AnonRateThrottle"],
    "DEFAULT_THROTTLE_RATES": {"anon": "120/min", "contact": "5/hour"},
}

CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = env_bool("SECURE_SSL_REDIRECT", False)
    SESSION_COOKIE_SECURE = env_bool("COOKIE_SECURE", True)
    CSRF_COOKIE_SECURE = env_bool("COOKIE_SECURE", True)
    SECURE_CONTENT_TYPE_NOSNIFF = True

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.getenv('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': os.getenv('CLOUDINARY_API_KEY'),
    'API_SECRET': os.getenv('CLOUDINARY_API_SECRET'),
}