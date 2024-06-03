#!/bin/sh

# Exit immediately if a command exits with a non-zero status
set -e

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Start the server and Celery beat
exec "$@"
