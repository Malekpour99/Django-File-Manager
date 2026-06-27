FROM python:3.13-alpine

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ARG VENV_PATH=/opt/venv

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_PROJECT_ENVIRONMENT=${VENV_PATH} \
    UV_NO_CACHE=1 \
    UV_PYTHON_DOWNLOADS=never

RUN apk add --no-cache ffmpeg

WORKDIR /app
COPY pyproject.toml uv.lock ./

RUN uv sync --no-editable --locked --no-dev

COPY ./app /app/
