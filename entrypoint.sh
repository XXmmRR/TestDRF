#!/bin/bash

while ! pg_isready -h db -p 5432 -q; do
  echo "Waiting for database..."
  sleep 1
done


echo "Collect static files"
uv run manage.py collectstatic --noinput

echo "Apply database migrations"

uv run manage.py migrate

uv run "$@"
