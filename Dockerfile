# syntax=docker/dockerfile:1
FROM python:3.13-alpine

# Install uv and uvx binaries from the Astral SH GitHub Container Registry
# COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
RUN pip install uv

# Set up environment variables for the virtual environment and Python settings
ARG VENV_PATH=/opt/venv

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

# Install ffmpeg for video processing
RUN apk add --no-cache ffmpeg

# Set the working directory for the application
WORKDIR /app

# Cache dependencies independently of application source changes.
COPY ./app/pyproject.toml ./app/uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-editable --locked --no-dev --no-install-project

# The project is not packaged; application modules run directly from /app.
COPY ./app .
