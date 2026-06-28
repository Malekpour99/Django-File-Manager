.PHONY: help setup build up down restart logs migrate superuser test lint shell clean

# Default target
help:
	@echo "Django File Manager - Available commands:"
	@echo ""
	@echo "  setup        Copy .env.example to .env (first time setup)"
	@echo "  build        Build Docker images"
	@echo "  up           Start all services in detached mode"
	@echo "  down         Stop and remove containers"
	@echo "  restart      Restart all services"
	@echo "  logs         Tail logs for all services"
	@echo "  migrate      Run database migrations"
	@echo "  superuser    Create a Django superuser"
	@echo "  test         Run the test suite"
	@echo "  lint         Run ruff linter"
	@echo "  shell        Open a Django shell"
	@echo "  clean        Stop containers and remove volumes"

setup:
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo ".env file created from .env.example — update it with your values before continuing."; \
	else \
		echo ".env already exists, skipping."; \
	fi

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

restart:
	docker compose restart

logs:
	docker compose logs -f

migrate:
	docker compose exec backend uv run python manage.py migrate

superuser:
	docker compose exec backend uv run python manage.py createsuperuser

test:
	docker compose exec backend uv run pytest .

lint:
	docker compose exec backend uv run ruff check .

shell:
	docker compose exec backend uv run python manage.py shell

clean:
	@read -p "This will remove all containers and volumes. Are you sure? [y/N] " confirm; \
	[ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ] || (echo "Aborted."; exit 1)
	docker compose down -v
