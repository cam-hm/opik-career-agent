#!/bin/bash
set -e

# Run migrations
alembic upgrade head

# Check for DB reset request
if [ "$RESET_DB_ON_STARTUP" = "true" ]; then
    echo "⚠️ RESETTING DATABASE AS REQUESTED BY ENV VAR..."
    python scripts/reset_db.py
fi

# Start app
uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
