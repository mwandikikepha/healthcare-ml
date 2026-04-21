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

# --- THE STABLE INSTALL METHOD ---
# 1. Install the heavy hitters first
RUN uv pip install --system "fastapi[standard]" "apache-airflow==2.10.2" "psycopg2-binary" "xgboost" "joblib"

# 2. If you have a requirements.txt or pyproject.toml, install the rest
# We use --system to bypass virtualenv requirement inside Docker
RUN if [ -f requirements.txt ]; then uv pip install --system -r requirements.txt; fi

# Set environment variables
ENV AIRFLOW_HOME=/app/airflow_home
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose ports
EXPOSE 8000 8080

# --- START COMMAND ---
# We use shell form to handle the background process for Airflow
CMD ["sh", "-c", "airflow standalone & fastapi run web/app.py --port 8000"]ecause they are in the system PATH
CMD ["sh", "-c", "airflow standalone & fastapi run web/app.py --port 8000"]
