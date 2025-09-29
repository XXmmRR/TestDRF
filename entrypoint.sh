#!/bin/bash

while ! pg_isready -h db -p 5432 -q; do
  echo "Waiting for database..."
  sleep 1
done


echo "Collect static files"
uv run manage.py collectstatic --noinput

echo "Apply database migrations"

uv run manage.py migrate

echo "Apply tests"
uv run pytest

if [ $? -ne 0 ]; then
    echo "Tests failed! Exiting."
    exit 1
fi

uv run "$@"
