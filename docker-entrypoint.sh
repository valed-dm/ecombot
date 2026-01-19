#!/bin/sh

# Exit immediately if a command exits with a non-zero status.
set -e

# Wait for the database to be ready
echo "Waiting for postgres at $PGHOST:$PGPORT..."

while ! nc -z $PGHOST $PGPORT; do
  sleep 0.1
done

echo "PostgreSQL started"

# Check if pyproject.toml exists
if [ -f "pyproject.toml" ]; then
    # Install poetry if not found
    if ! command -v poetry > /dev/null 2>&1; then
        echo "Poetry not found. Installing..."
        pip install poetry
    fi

    # Ensure dependencies are up to date
    echo "Installing dependencies..."
    poetry install --no-interaction
else
    echo "Skipping dependency installation (Production mode)"
fi

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

# Seed default data (Pickup Point)
echo "Seeding default pickup point..."
python src/ecombot/bot/handlers/checkout/seed_pickup.py

# Start the application
echo "Starting application..."
exec "$@"
