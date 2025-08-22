#!/bin/bash
set -e

echo "Starting Superset setup..."

# Upgrade DB & init Superset metadata
superset db upgrade
superset init

# Create admin user if not exists
if ! superset fab list-users | grep -q "${ADMIN_USERNAME:-admin}"; then
  echo "Creating admin user..."
  superset fab create-admin \
    --username "${ADMIN_USERNAME:-admin}" \
    --firstname "${ADMIN_FIRST_NAME:-Admin}" \
    --lastname "${ADMIN_LAST_NAME:-User}" \
    --email "${ADMIN_EMAIL:-admin@example.com}" \
    --password "${ADMIN_PASSWORD:-admin}"
else
  echo "Admin user already exists, skipping creation."
fi

# Run the Superset server with Gunicorn for production
exec gunicorn --workers 3 --timeout 120 --bind 0.0.0.0:8088 "superset.app:create_app()"
