# Django-File-Manager

A file manager project built with Django and template rendering.

## Features

- Customized user and profile
- Uploading images and videos
- Validation for uploaded files (format & size)
- Creating new folders
- Using nested structure for your files and folders
- Search through your files and folders
- Deleting files and folders
- Up and running Celery & Redis
- Customized logging
- Customized caching based on Redis
- smtp4dev development mailing service

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) & Docker Compose
- `make` (pre-installed on Linux/macOS; Windows users can use [WSL](https://learn.microsoft.com/en-us/windows/wsl/) or [Make for Windows](https://gnuwin32.sourceforge.net/packages/make.htm))

## Quick Start

```sh
make setup   # copies .env.example → .env (edit it with your values first)
make build   # build Docker images
make up      # start all services
make migrate # run database migrations
```

## Docker Images

Compose builds the `development` target, including pytest and Ruff. Commands use
installed executables directly; dependencies are installed only during the build.
Rebuild with `make build` and recreate containers with `make up` after changing
`pyproject.toml` or `uv.lock`.

The default Dockerfile target is `production`, containing production dependencies
and using Gunicorn. Build it with:

```sh
docker build --target production -t django-file-manager:production .
```

Deploy this image with environment variables for `core.django.production` or
`core.django.stage`. The Compose file remains the local development configuration.
Both targets run as UID/GID 1000 and keep dependencies in `/opt/venv`, outside the
`/app` development bind mount. Bind-mounted files and writable data volumes must
have permissions for this user. Celery Beat stores its schedule in the
`celerybeat-data` volume.

## Available Make Commands

| Command                    | Description                                      |
| -------------------------- | ------------------------------------------------ |
| `make help`                | List all available commands                      |
| `make setup`               | Copy `.env.example` to `.env` (first-time setup) |
| `make build`               | Build Docker images                              |
| `make up`                  | Start all services in detached mode              |
| `make down`                | Stop and remove containers                       |
| `make restart`             | Restart all services                             |
| `make logs`                | Tail logs for all services                       |
| `make logs service=<name>` | Tail logs for a specific service                 |
| `make migrate`             | Run database migrations                          |
| `make superuser`           | Create a Django superuser                        |
| `make test`                | Run the test suite                               |
| `make lint`                | Run ruff linter                                  |
| `make shell`               | Open a Django shell                              |
| `make clean`               | Stop containers and remove volumes               |

## Configuration

Settings follow [HackSoft's Django Styleguide](https://github.com/HackSoftware/Django-Styleguide#settings), retaining the existing `core` package and `python-decouple` dependency:

```text
app/core/
├── env.py                 # shared environment reader
├── django/
│   ├── base.py            # Django settings; imports every integration
│   ├── local.py           # development defaults
│   ├── production.py      # deployment checks and HTTPS defaults
│   ├── stage.py           # production defaults for staging
│   └── test.py            # isolated test backends
└── settings/              # storage, caching, Celery, CORS, email, logging, DRF
```

Edit `.env` before starting. Fill in `DJANGO_DB_PASSWORD`, matching
`POSTGRES_PASSWORD`, and the MinIO access/secret keys. Set a strong
`DJANGO_SECRET_KEY` for deployment. `.env` is read from the repository root
locally; Docker Compose passes its values to containers. Process variables take
precedence over `.env` values with the same name.

`manage.py` and Celery default to `core.django.local`; WSGI and ASGI default to
`core.django.production`. Set `DJANGO_SETTINGS_MODULE` in the process environment
to override these defaults. The Compose `.env.example` selects local settings.
When running outside Compose, export this variable explicitly or pass
`--settings=core.django.production` to management commands; Django chooses its
settings module before loading the settings `.env` reader.

Django-specific variables use the `DJANGO_` prefix. Previous names (`SECRET_KEY`,
`DEBUG`, `ALLOWED_HOSTS`, `LOG_LEVEL`, and `DB_*`) remain accepted outside tests,
with prefixed names taking priority. Replace any references to the former
`core.settings` module with the appropriate `core.django.*` module.

For staging, set `DJANGO_SETTINGS_MODULE=core.django.stage` in the process
environment (or the Compose `.env`). Stage inherits production settings; supply
separate staging credentials, database, storage buckets, Redis databases, and
allowed hosts through environment variables.

Production and stage force debug off, require a nonempty secret and explicit allowed
hosts, and defaults to HTTPS redirects and secure cookies. Configure TLS and
static/media serving in your deployment. HSTS is opt-in through
`DJANGO_SECURE_HSTS_SECONDS`; enable it after HTTPS is verified. If TLS terminates
at a proxy, configure Django's proxy SSL handling for your trusted proxy before
enabling redirects.

Pytest selects `core.django.test`, ignores the local `.env` and legacy variable
names, and uses SQLite, in-memory file storage/cache/email, fast password hashing,
and eager Celery tasks. It requires no running external services. Run locally
from `app/` with `../.venv/bin/pytest` (or `uv run pytest` with dev dependencies).
SQLite tests do not validate PostgreSQL-specific behavior.

## Creating a Superuser

```sh
make superuser
```

Log in with superuser credentials to access the Django admin panel at `/admin/`.

## Running Tests

```sh
make test
```

Add your own tests alongside the existing ones to extend coverage.

## Linting

```sh
make lint
```

Uses [ruff](https://docs.astral.sh/ruff/) for fast Python linting.
