FROM python:3.13.7-slim-bookworm

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/app/.venv

RUN apt-get update && apt-get install -y build-essential

COPY pyproject.toml uv.lock ./

RUN pip install uv && \
    uv sync --cache-dir /opt/uv-cache

EXPOSE 8000

COPY . /app

