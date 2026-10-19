from core.env import env

USE_REDIS_CACHE = env("USE_REDIS_CACHE", default=False, cast=bool)
CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
if USE_REDIS_CACHE:
    REDIS_CACHE_URL = env("REDIS_CACHE_URL")
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": REDIS_CACHE_URL,
            "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
        }
    }
