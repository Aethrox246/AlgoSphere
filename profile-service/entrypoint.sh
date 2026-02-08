#!/bin/sh
set -e

# Force-add /app/src to PYTHONPATH BEFORE anything else
export PYTHONPATH="/app/src:$PYTHONPATH"

echo "PYTHONPATH set to: $PYTHONPATH"
echo "Current dir: $(pwd)"
echo "Listing /app/src:"
ls -la /app/src

# Run Alembic migrations if they exist
if [ -f alembic.ini ]; then
  echo "Running Alembic migrations..."
  alembic upgrade head || echo "Migrations skipped or failed - continuing"
fi

# Start Uvicorn
echo "Starting Uvicorn..."
exec uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload