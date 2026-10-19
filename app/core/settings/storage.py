"""Local storage by default; MinIO credentials are required only when enabled."""

from core.env import env

USE_MINIO = env("USE_MINIO", default=False, cast=bool)
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}

if USE_MINIO:
    STORAGES = {
        "default": {
            "BACKEND": "minio_storage.storage.MinioMediaStorage",
        },
        "staticfiles": {
            "BACKEND": "minio_storage.storage.MinioStaticStorage",
        },
    }

    # Minio - global config
    MINIO_STORAGE_ENDPOINT = env("MINIO_STORAGE_ENDPOINT")
    MINIO_EXTERNAL_STORAGE_ENDPOINT = env("MINIO_EXTERNAL_STORAGE_ENDPOINT")

    # Minio - security config
    MINIO_STORAGE_ACCESS_KEY = env("MINIO_STORAGE_ACCESS_KEY")
    MINIO_STORAGE_SECRET_KEY = env("MINIO_STORAGE_SECRET_KEY")
    MINIO_STORAGE_USE_HTTPS = env("MINIO_STORAGE_USE_HTTPS", cast=bool)

    # Minio - media files config
    MINIO_STORAGE_MEDIA_BUCKET_NAME = env(
        "MINIO_STORAGE_MEDIA_BUCKET_NAME", default="media"
    )
    MINIO_STORAGE_MEDIA_USE_PRESIGNED = True
    MINIO_STORAGE_AUTO_CREATE_MEDIA_BUCKET = True

    # Minio - static files config
    MINIO_STORAGE_STATIC_BUCKET_NAME = env(
        "MINIO_STORAGE_STATIC_BUCKET_NAME", default="static"
    )
    MINIO_STORAGE_STATIC_USE_PRESIGNED = False
    MINIO_STORAGE_AUTO_CREATE_STATIC_BUCKET = True

    # changing base url schema for static and media serve
    # by default in dev mode it will look for localhost port 9000 you can configure another when using online
    MINIO_STORAGE_STATIC_URL = env(
        "MINIO_STORAGE_STATIC_URL",
        f"{MINIO_EXTERNAL_STORAGE_ENDPOINT}/{MINIO_STORAGE_STATIC_BUCKET_NAME}",
    )
    MINIO_STORAGE_MEDIA_URL = env(
        "MINIO_STORAGE_MEDIA_URL",
        f"{MINIO_EXTERNAL_STORAGE_ENDPOINT}/{MINIO_STORAGE_MEDIA_BUCKET_NAME}",
    )
