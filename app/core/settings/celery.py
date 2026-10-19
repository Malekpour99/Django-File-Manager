from core.env import env

USE_CELERY = env("USE_CELERY", default=False, cast=bool)
CELERY_TASK_ALWAYS_EAGER = not USE_CELERY
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_BROKER_URL = env("CELERY_BROKER_URL") if USE_CELERY else "memory://"
