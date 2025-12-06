#!/usr/bin/env bash
set -e

# Wait for Postgres (optional but helpful in compose)
if [ -n "${DB_HOST}" ]; then
  echo "Waiting for Postgres at ${DB_HOST}:${DB_PORT:-5432}..."
  until nc -z "${DB_HOST}" "${DB_PORT:-5432}"; do
    sleep 0.5
  done
fi

# Run migrations (requires alembic.ini to use ${DATABASE_URL})
echo "Running Alembic migrations..."
export PATH="$PATH:/home/app/.local/bin"
alembic upgrade head

echo "Starting FastAPI..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
