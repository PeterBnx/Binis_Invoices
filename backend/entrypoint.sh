#!/bin/sh

# Exit immediately if a command exits with a non-zero status
set -e

echo "Running Migrations..."
python manage.py migrate --noinput

echo "Starting Server..."
exec "$@"