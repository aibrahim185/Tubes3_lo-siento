#!/bin/bash

# Docker startup script for ATS CV Analyzer
# This script handles the initialization and startup of the application in Docker

echo "Starting ATS CV Analyzer..."

# Wait for MySQL to be ready
echo "Waiting for MySQL to be ready..."
while ! mysqladmin ping -h"$DB_HOST" -P"$DB_PORT" -u"$DB_USER" -p"$DB_PASSWORD" --silent; do
    echo "MySQL is unavailable - sleeping"
    sleep 2
done

echo "MySQL is ready!"

# Create necessary directories
mkdir -p /app/data /app/logs

# Set proper permissions
chmod -R 755 /app/data /app/logs

# Run database migrations/setup if needed
echo "Setting up database..."
python -c "
from src.db.database_manager import db_manager
import logging

logging.basicConfig(level=logging.INFO)

try:
    if db_manager.connect():
        print('Database connected successfully!')
        db_manager.disconnect()
    else:
        print('Failed to connect to database!')
        exit(1)
except Exception as e:
    print(f'Database setup error: {e}')
    exit(1)
"

echo "Database setup complete!"

# Start the application
echo "Starting ATS CV Analyzer application..."
exec python src/main.py
