#!/bin/sh

if python3 run_migration.py 2>&1; then
  uvicorn app.asgi:app --host 0.0.0.0 --port 8000
else
    echo "an error occurred while starting application."
    exit 1
fi
