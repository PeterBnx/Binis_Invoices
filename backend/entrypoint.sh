#!/bin/sh
set -e

echo "Running Migrations..."
python manage.py migrate --noinput

echo "Creating Admin User..."
python create_admin.py

echo "Starting Server..."
exec "$@"