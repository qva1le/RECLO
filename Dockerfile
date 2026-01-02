# Dockerfile (clean + stable)
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

WORKDIR /app

# system deps (минимум + компилятор на случай wheels)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
  && rm -rf /var/lib/apt/lists/*

# Poetry
RUN pip install --no-cache-dir poetry

# deps first (кэшируется)
COPY pyproject.toml poetry.lock* /app/

# install deps (no dev)
RUN poetry install --no-root --only main

# ✅ HARD FIX: remove any mixed/old redis files and reinstall correct redis
RUN python -m pip uninstall -y redis || true \
 && rm -rf /usr/local/lib/python3.12/site-packages/redis \
 && rm -rf /usr/local/lib/python3.12/site-packages/redis-*.dist-info \
 && python -m pip install --no-cache-dir --force-reinstall "redis==5.3.1"

# code
COPY . /app

# non-root
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
