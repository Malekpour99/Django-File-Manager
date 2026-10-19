from core.env import env

EMAIL_BACKEND = env(
    "DJANGO_EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend"
)
EMAIL_HOST = env("DJANGO_EMAIL_HOST", default="localhost")
EMAIL_PORT = env("DJANGO_EMAIL_PORT", default=25, cast=int)
EMAIL_USE_TLS = env("DJANGO_EMAIL_USE_TLS", default=False, cast=bool)
EMAIL_USE_SSL = env("DJANGO_EMAIL_USE_SSL", default=False, cast=bool)
EMAIL_HOST_USER = env("DJANGO_EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("DJANGO_EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = env("DJANGO_DEFAULT_FROM_EMAIL", default="webmaster@localhost")
