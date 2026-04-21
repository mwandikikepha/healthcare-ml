# Use a slim Python 3.12 image
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install 'uv'
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy project files
COPY . .

# --- THE FIXES ---
# 1. Force install fastapi[standard] and apache-airflow
# 2. Sync everything
RUN uv pip install "fastapi[standard]" apache-airflow
RUN uv sync

# Set environment variables
ENV AIRFLOW_HOME=/app/airflow_home
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose ports
EXPOSE 8000 8080

# --- THE FIX FOR SPAWNING ---
# We use 'uv run' explicitly for both to ensure the virtualenv is used
CMD ["sh", "-c", "uv run airflow standalone & uv run fastapi run web/app.py --port 8000"]