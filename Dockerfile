FROM python:3.13-alpine

# Install uv and uvx binaries from the Astral SH GitHub Container Registry
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set up environment variables for the virtual environment and Python settings
ARG VENV_PATH=/opt/venv

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_PROJECT_ENVIRONMENT=${VENV_PATH} \
    UV_NO_CACHE=1 \
    UV_PYTHON_DOWNLOADS=never

# Install ffmpeg for video processing
RUN apk add --no-cache ffmpeg

# Set the working directory for the application
WORKDIR /app

# Copy project dependencies
COPY pyproject.toml uv.lock ./

# Install project dependencies
RUN uv sync --no-editable --locked --no-dev

# Copy the application code into the container
COPY ./app /app/
