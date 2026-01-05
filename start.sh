#!/bin/bash

# Run database migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Start the application
echo "Starting application..."
python -m gunicorn hr_portal.wsgi
