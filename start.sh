#!/usr/bin/env bash
set -euo pipefail

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static..."
python manage.py collectstatic --noinput

if [[ -n "${HR_BOOTSTRAP_ADMIN_ID:-}" ]]; then
  echo "Bootstrapping first admin (idempotent)..."
  admin_name="${HR_BOOTSTRAP_ADMIN_NAME:-HR Admin}"
  if [[ -n "${HR_BOOTSTRAP_ADMIN_PASSWORD:-}" ]]; then
    python manage.py bootstrap_admin --employee-id "${HR_BOOTSTRAP_ADMIN_ID}" --name "${admin_name}" --password "${HR_BOOTSTRAP_ADMIN_PASSWORD}"
  else
    python manage.py bootstrap_admin --employee-id "${HR_BOOTSTRAP_ADMIN_ID}" --name "${admin_name}"
  fi
fi

echo "Starting Gunicorn..."
exec gunicorn hr_portal.wsgi:application \
  --bind "0.0.0.0:${PORT:-8000}" \
  --workers "${WEB_CONCURRENCY:-2}"


