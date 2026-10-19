"""Production overrides. Set DJANGO_SETTINGS_MODULE explicitly when deploying."""

from django.core.exceptions import ImproperlyConfigured

from core.django.base import *  # noqa: F403
from core.env import Csv, env

DEBUG = False
if not SECRET_KEY or SECRET_KEY.startswith("django-insecure-"):  # noqa: F405
    raise ImproperlyConfigured("Set DJANGO_SECRET_KEY to a secure production secret.")
ALLOWED_HOSTS = env(
    "DJANGO_ALLOWED_HOSTS", default="", cast=Csv(), legacy="ALLOWED_HOSTS"
)
if not ALLOWED_HOSTS or "*" in ALLOWED_HOSTS:
    raise ImproperlyConfigured("Set DJANGO_ALLOWED_HOSTS to explicit production hosts.")

SESSION_COOKIE_SECURE = env("DJANGO_SESSION_COOKIE_SECURE", default=True, cast=bool)
CSRF_COOKIE_SECURE = env("DJANGO_CSRF_COOKIE_SECURE", default=True, cast=bool)
SECURE_SSL_REDIRECT = env("DJANGO_SECURE_SSL_REDIRECT", default=True, cast=bool)
SECURE_HSTS_SECONDS = env("DJANGO_SECURE_HSTS_SECONDS", default=0, cast=int)
SECURE_HSTS_INCLUDE_SUBDOMAINS = env(
    "DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS", default=False, cast=bool
)
SECURE_HSTS_PRELOAD = env("DJANGO_SECURE_HSTS_PRELOAD", default=False, cast=bool)
