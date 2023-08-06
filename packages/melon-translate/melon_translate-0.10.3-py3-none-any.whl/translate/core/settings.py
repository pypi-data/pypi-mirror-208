from pathlib import Path

import sentry_sdk
from decouple import config
from sentry_sdk.integrations.django import DjangoIntegration

from translate.service.utils.version_handler import extract_version

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

VERSION_TAG = extract_version()

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-yq@*8hm7=0d1mi@lqnnmh$qalu0uv0@m1a0e!_1o09wt%++4^k"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config("DEBUG", cast=bool, default=True)

ALLOWED_HOSTS = ["*"]

sentry_sdk.init(
    dsn=config(
        "SENTRY_TRANSLATE_DNS", cast=str, default="https://0692b182605640f982720e655d3f2001@sentry.dev.getmelon.dev/3"
    ),
    integrations=[
        DjangoIntegration(),
    ],
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0,
    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True,
)


TRANSLATE_ADDRESS = config("TRANSLATE_ADDRESS", cast=str, default="http://localhost")
TRANSLATE_PORT = config("TRANSLATE_PORT", cast=int, default="8000")

# Application definition

INSTALLED_APPS = [
    "baton",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_admin_inline_paginator",
    "auditlog",
    "rest_framework",
    "drf_spectacular",
    "translate.service",
    "health_check",
    "health_check.db",
    "health_check.cache",
    "health_check.storage",
    "health_check.contrib.migrations",
    "baton.autodiscover",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.gzip.GZipMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "auditlog.middleware.AuditlogMiddleware",
]

ROOT_URLCONF = "translate.core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            "translate/service/templates/",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "translate.core.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("POSTGRES_DB", default="melon_translate"),
        "USER": config("POSTGRES_USER", default="melon_user"),
        "PASSWORD": config("POSTGRES_PASSWORD", default="melonmelon!"),
        "HOST": config("POSTGRES_HOST", default="127.0.0.1", cast=str),
        "PORT": config("POSTGRES_PORT", cast=int, default=5432),
        "CONN_MAX_AGE": config("POSTGRES_CONN_MAX_AGE", cast=int, default=600),
    },
}

REDIS_HOST = config("REDIS_HOST", cast=str, default="127.0.0.1")
REDIS_PORT = config("REDIS_PORT", cast=int, default=6379)
REDIS_DB = config("REDIS_DATABASE", cast=int, default=0)

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

CACHE_TTL = 60 * 45
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

# CSRF settings
CSRF_TRUSTED_ORIGINS = config(
    "CSRF_TRUSTED_ORIGINS", cast=lambda v: [s.strip() for s in v.split(",")], default="http://localhost"
)

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files

STATIC_ROOT = (Path(BASE_DIR) / "assets").as_posix()

STATIC_URL = "/static/"


# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PAGINATION_CLASS": "translate.service.paginations.TranslateClientPagination",
    "PAGE_SIZE": 500,  # default value if not set in paginator
}

SPECTACULAR_SETTINGS = {
    "TITLE": "melon-translate",
    "DESCRIPTION": "Translation microservice",
    "VERSION": VERSION_TAG,
}

BATON = {
    "SITE_HEADER": "Melon-translate",
    "SITE_TITLE": "Melon-translate",
    "INDEX_TITLE": "Translations administration",
    "SUPPORT_HREF": "https://github.com/",
    "COPYRIGHT": 'Copyright © 2022 <a href="https://www.emonitor.ch">eMonitor</a>',  # noqa
    "POWERED_BY": '<a href="https://www.emonitor.ch">eMonitor</a>',
    "CONFIRM_UNSAVED_CHANGES": True,
    "SHOW_MULTIPART_UPLOADING": True,
    "ENABLE_IMAGES_PREVIEW": True,
    "CHANGELIST_FILTERS_IN_MODAL": True,
    "CHANGELIST_FILTERS_ALWAYS_OPEN": False,
    "CHANGELIST_FILTERS_FORM": True,
    "MENU_ALWAYS_COLLAPSED": False,
    "MENU_TITLE": "Menu",
    "MESSAGES_TOASTS": False,
    "GRAVATAR_DEFAULT_IMG": "retro",
    "LOGIN_SPLASH": f"{STATIC_URL}assets/img/swiss_flg.jpeg",
    "SEARCH_FIELD": {
        "label": "Search contents...",
        "url": "/search/",
    },
    "MENU": (
        {"type": "title", "label": "main", "apps": ("auth",)},
        {
            "type": "app",
            "name": "auth",
            "label": "Authentication",
            "icon": "fa fa-lock",
            "models": (
                {"name": "user", "label": "Users"},
                {"name": "group", "label": "Groups"},
            ),
        },
        {"type": "title", "label": "service"},
        {
            "type": "free",
            "name": "translate.service",
            "label": "Translation service",
            "icon": "fa fa-sign",
            "url": "/admin/service/",
        },
        {
            "type": "free",
            "label": "Add New Translation Key",
            "default_open": True,
            "icon": "fa fa-key",
            "url": "/admin/service/translationkey/add/",
        },
        {
            "type": "free",
            "name": "context",
            "label": "Usage context input",
            "icon": "fa fa-graduation-cap",
            "url": "/admin/service/translationkey/?context-input=context-not-inserted/",
        },
        {
            "type": "free",
            "name": "health",
            "label": "Health check",
            "icon": "fa fa-heart",
            "url": "/health/",
        },
        {
            "type": "free",
            "name": "redoc",
            "label": "Redoc schema docs",
            "icon": "fa fa-book",
            "url": "/api/schema/redoc/",
        },
    ),
}

SILENCED_SYSTEM_CHECKS = [
    "django_jsonfield_backport.W001",
]
