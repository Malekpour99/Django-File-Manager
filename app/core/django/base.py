"""Shared Django settings. Every integration is composed here."""

from django.urls import reverse_lazy

from core.env import BASE_DIR, Csv, env

SECRET_KEY = env("DJANGO_SECRET_KEY", default="", legacy="SECRET_KEY")
DEBUG = env("DJANGO_DEBUG", default=False, cast=bool, legacy="DEBUG")
ALLOWED_HOSTS = env(
    "DJANGO_ALLOWED_HOSTS",
    default="localhost,127.0.0.1,[::1]",
    cast=Csv(),
    legacy="ALLOWED_HOSTS",
)

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]
THIRD_PARTY_APPS = [
    "corsheaders",
    "rest_framework",
    "rest_framework.authtoken",
    "rest_framework_simplejwt",
    "django_filters",
    "drf_yasg",
    "mail_templated",
]
LOCAL_APPS = ["accounts", "filemanager"]
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",
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

WSGI_APPLICATION = "core.wsgi.application"


ASGI_APPLICATION = "core.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("DJANGO_DB_NAME", default="filemanager", legacy="DB_NAME"),
        "USER": env("DJANGO_DB_USER", default="filemanager", legacy="DB_USER"),
        "PASSWORD": env("DJANGO_DB_PASSWORD", default="", legacy="DB_PASSWORD"),
        "HOST": env("DJANGO_DB_HOST", default="localhost", legacy="DB_HOST"),
        "PORT": env("DJANGO_DB_PORT", default="5432", legacy="DB_PORT"),
    }
}

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


STATIC_URL = "/static/"
MEDIA_URL = "/media/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_ROOT = BASE_DIR / "media"
STATICFILES_DIRS = [BASE_DIR / "statics"]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "accounts.User"
LOGIN_REDIRECT_URL = reverse_lazy("filemanager:home")

# All integrations are imported in every environment. Flags control activation.
from core.settings.caching import *  # noqa: E402,F403
from core.settings.celery import *  # noqa: E402,F403
from core.settings.cors import *  # noqa: E402,F403
from core.settings.email import *  # noqa: E402,F403
from core.settings.logging import *  # noqa: E402,F403
from core.settings.rest_framework import *  # noqa: E402,F403
from core.settings.storage import *  # noqa: E402,F403

if USE_MINIO:  # noqa: F405
    INSTALLED_APPS += ["minio_storage"]
