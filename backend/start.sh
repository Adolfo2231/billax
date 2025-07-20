#!/bin/bash

echo "Starting Billax API..."

# Set default port if not provided
export PORT=${PORT:-5000}

# Run database migrations if DATABASE_URL is set
if [ ! -z "$DATABASE_URL" ]; then
    echo "Running database migrations..."
    cd /app
    python -m flask db upgrade
    echo "Migrations completed."
else
    echo "No DATABASE_URL set, skipping migrations."
fi

# Start the application with gunicorn
echo "Starting application on port $PORT..."
exec gunicorn run:app \
    --bind 0.0.0.0:$PORT \
    --workers 1 \
    --timeout 120 \
    --preload \
    --access-logfile - \
    --error-logfile - \
    --log-level info # Force redeploy
