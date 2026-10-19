from core.env import Csv, env

CORS_ALLOW_ALL_ORIGINS = env("DJANGO_CORS_ALLOW_ALL_ORIGINS", default=False, cast=bool)
CORS_ALLOWED_ORIGINS = env("DJANGO_CORS_ALLOWED_ORIGINS", default="", cast=Csv())
CSRF_TRUSTED_ORIGINS = env("DJANGO_CSRF_TRUSTED_ORIGINS", default="", cast=Csv())
