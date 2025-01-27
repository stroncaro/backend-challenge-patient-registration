#!/bin/bash

# Start Redis
echo "Starting Redis..."
redis-server &

# Wait for Redis to be available
echo "Waiting for Redis..."
while ! nc -z localhost 6379; do
  sleep 1
done

echo "Redis is up, starting FastAPI and Celery..."

# Start Celery
cd src
celery -A background_tasks worker --loglevel=info &

# Start FastAPI in the background
fastapi dev main.py --host 0.0.0.0
