#!/bin/sh

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Run the main command
exec "$@"
