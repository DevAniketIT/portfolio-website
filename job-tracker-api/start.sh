#!/bin/bash

# Job Application Tracker API Production Startup Script
# This script handles database migrations and starts the application server

set -e  # Exit on any error

echo "🚀 Starting Job Application Tracker API..."

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in production environment
if [ "$ENVIRONMENT" = "production" ]; then
    print_status "Running in PRODUCTION mode"
else
    print_warning "Environment not set to production. Current: ${ENVIRONMENT:-'not set'}"
fi

# Check if required environment variables are set
print_status "Checking environment variables..."
if [ -z "$DATABASE_URL" ]; then
    print_error "DATABASE_URL environment variable is not set!"
    exit 1
fi

if [ -z "$PORT" ]; then
    print_warning "PORT not set, defaulting to 8000"
    export PORT=8000
fi

print_status "Database URL: ${DATABASE_URL%@*}@***" # Hide password in logs
print_status "Server will start on port: $PORT"

# Wait for database to be ready (optional, but recommended)
print_status "Waiting for database to be ready..."
python -c "
import time
import psycopg2
import os
from urllib.parse import urlparse

def wait_for_db():
    db_url = os.environ['DATABASE_URL']
    parsed = urlparse(db_url)
    
    max_attempts = 30
    attempt = 0
    
    while attempt < max_attempts:
        try:
            conn = psycopg2.connect(
                host=parsed.hostname,
                port=parsed.port or 5432,
                user=parsed.username,
                password=parsed.password,
                database=parsed.path[1:] if parsed.path else 'postgres'
            )
            conn.close()
            print('✅ Database is ready!')
            return True
        except psycopg2.OperationalError as e:
            attempt += 1
            print(f'⏳ Waiting for database... (attempt {attempt}/{max_attempts})')
            time.sleep(2)
    
    raise Exception('Database is not available after 60 seconds')

wait_for_db()
"

if [ $? -ne 0 ]; then
    print_error "Database is not available. Exiting."
    exit 1
fi

# Initialize database (create tables if they don't exist)
print_status "Initializing database tables..."
python -c "
import os
import sys
import logging
from postgresql_db import initialize_postgresql_database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    logger.info('Creating database tables...')
    db = initialize_postgresql_database(os.environ['DATABASE_URL'])
    logger.info('✅ Database initialized successfully')
except Exception as e:
    logger.error(f'❌ Database initialization failed: {e}')
    sys.exit(1)
"

if [ $? -ne 0 ]; then
    print_error "Database initialization failed. Exiting."
    exit 1
fi

# Optional: Run any data migrations or seed data
# Uncomment this section if you have migration scripts
# print_status "Running data migrations..."
# python migrate.py

print_status "Database setup completed successfully!"

# Set production-optimized server settings
export WORKERS=${WORKERS:-1}  # Number of worker processes
export WORKER_CLASS=${WORKER_CLASS:-"uvicorn.workers.UvicornWorker"}
export MAX_REQUESTS=${MAX_REQUESTS:-1000}  # Restart workers after N requests
export MAX_REQUESTS_JITTER=${MAX_REQUESTS_JITTER:-50}
export TIMEOUT=${TIMEOUT:-120}  # Worker timeout
export KEEPALIVE=${KEEPALIVE:-2}  # Keep-alive timeout

print_status "Starting server with the following configuration:"
print_status "  Workers: $WORKERS"
print_status "  Worker Class: $WORKER_CLASS"
print_status "  Max Requests: $MAX_REQUESTS"
print_status "  Timeout: $TIMEOUT seconds"
print_status "  Keep-alive: $KEEPALIVE seconds"

# Start the FastAPI application with production settings
print_status "🎯 Launching FastAPI application..."

# Option 1: Using Uvicorn directly (recommended for Render)
exec uvicorn main:app \
    --host 0.0.0.0 \
    --port $PORT \
    --workers $WORKERS \
    --access-log \
    --log-level info \
    --timeout-keep-alive $KEEPALIVE \
    --loop uvloop \
    --http httptools

# Option 2: Using Gunicorn (alternative, uncomment if preferred)
# exec gunicorn main:app \
#     --bind 0.0.0.0:$PORT \
#     --workers $WORKERS \
#     --worker-class $WORKER_CLASS \
#     --max-requests $MAX_REQUESTS \
#     --max-requests-jitter $MAX_REQUESTS_JITTER \
#     --timeout $TIMEOUT \
#     --keep-alive $KEEPALIVE \
#     --log-level info \
#     --access-logfile - \
#     --error-logfile -
