#!/usr/bin/env sh
set -eu

max_attempts="${MIGRATION_MAX_ATTEMPTS:-20}"
sleep_seconds="${MIGRATION_RETRY_SLEEP_SECONDS:-3}"
attempt=1

mkdir -p alembic/versions

echo "Running migration bootstrap..."
while :; do
  if [ -z "$(find alembic/versions -maxdepth 1 -type f -name '*.py' -print -quit)" ]; then
    echo "No migration files found. Generating init migration..."
    uv run alembic revision --autogenerate -m "init"
  fi

  if uv run alembic upgrade head; then
    break
  fi

  if uv run alembic current 2>&1 | grep -q "Can't locate revision identified by"; then
    echo "Database points to a missing revision. Stamping database to current head..."
    uv run alembic stamp head
    uv run alembic upgrade head
    break
  fi

  if [ "$attempt" -ge "$max_attempts" ]; then
    echo "Migration failed after ${attempt} attempts."
    exit 1
  fi
  echo "Migration attempt ${attempt}/${max_attempts} failed. Retrying in ${sleep_seconds}s..."
  attempt=$((attempt + 1))
  sleep "$sleep_seconds"
done

echo "Starting backend server..."
exec uv run uvicorn main:app --host 0.0.0.0 --port 8000
