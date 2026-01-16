#!/bin/sh

# Exit immediately if a command exits with a non-zero status.
set -e

# Wait for the database to be ready
echo "Waiting for postgres at $PGHOST:$PGPORT..."

while ! nc -z $PGHOST $PGPORT; do
  sleep 0.1
done

echo "PostgreSQL started"

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

# Seed default data (Pickup Point)
echo "Seeding default pickup point..."
python src/ecombot/bot/handlers/checkout/seed_pickup.py

# Start the application
echo "Starting application..."
exec "$@"
