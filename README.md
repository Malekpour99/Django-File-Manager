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

Edit the generated `.env` file with your own values before starting the project. Refer to `.env.example` for available options.

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
