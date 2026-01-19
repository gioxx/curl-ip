FROM python:3.15.0a5-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --disable-pip-version-check --prefer-binary -r requirements.txt

COPY app.py /app/app.py

# Create non-root user
RUN useradd --create-home --uid 10001 appuser && chown -R appuser:appuser /app
USER appuser

# Config (override at runtime)
ENV ENABLE_DEBUG=false
# Pass DEBUG_TOKEN at runtime: -e DEBUG_TOKEN=...

# Expose service port
EXPOSE 8080

# Optional: container healthcheck hitting "/"
# (Assumes curl present; if not, install or remove this block)
# RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*
# HEALTHCHECK --interval=30s --timeout=3s --retries=3 CMD curl -fsS http://localhost:8080/ || exit 1

# Start with Gunicorn (1 worker per CPU core is common; keep it simple here)
# app: Flask instance is created in app.py as `app`
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--threads", "2", "--timeout", "30", "app:app"]
