"""Local development; integrations are selected through environment variables."""

from core.django.base import *  # noqa: F403
from core.env import env

DEBUG = env("DJANGO_DEBUG", default=True, cast=bool, legacy="DEBUG")
SECRET_KEY = SECRET_KEY or "django-insecure-local-development-only"  # noqa: F405
