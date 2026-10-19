# syntax=docker/dockerfile:1
FROM ghcr.io/astral-sh/uv:0.13.1 AS uv

FROM python:3.13-alpine AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    PATH="/opt/venv/bin:$PATH"

RUN apk add --no-cache ffmpeg \
    && addgroup -g 1000 app \
    && adduser -D -u 1000 -G app app \
    && mkdir -p /app/media /app/staticfiles /var/lib/celery \
    && chown app:app /app/media /app/staticfiles /var/lib/celery

WORKDIR /app

FROM base AS dependencies
COPY --from=uv /uv /usr/local/bin/uv
COPY ./app/pyproject.toml ./app/uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev --no-install-project

FROM dependencies AS development-dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project

FROM base AS development
COPY --from=development-dependencies /opt/venv /opt/venv
COPY ./app .
USER app
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

FROM base AS production
COPY --from=dependencies /opt/venv /opt/venv
COPY ./app .
ENV DJANGO_SETTINGS_MODULE=core.django.production
USER app
EXPOSE 8000
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000", "--access-logfile", "-", "--error-logfile", "-"]
