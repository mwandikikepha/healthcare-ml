# Use a slim Python 3.12 image
FROM python:3.12-slim

# Install system dependencies for Postgres, SSL, and build tools
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory to the root of your project
WORKDIR /app

# Install 'uv' for high-speed package management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy all project files into the container
COPY . .

# --- DEPENDENCY INSTALLATION ---
# 1. Install core services and drivers into the system environment

RUN uv pip install --system \
    "fastapi[standard]" \
    "apache-airflow==2.10.2" \
    "sqlalchemy<2.0" \
    "psycopg2-binary" \
    "xgboost" \
    "joblib" \
    "uvicorn"

# 2. Install any additional requirements from your files
RUN if [ -f requirements.txt ]; then uv pip install --system -r requirements.txt; fi

# --- CONFIGURATION ---
# Define Airflow and Python paths
ENV AIRFLOW_HOME=/app/airflow_home
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Create the Airflow Home directory and link your DAGs folder
RUN mkdir -p /app/airflow_home && \
    ln -s /app/airflow/dags /app/airflow_home/dags

# Expose ports for FastAPI (8000) and Airflow (8080)
EXPOSE 8000 8080

# --- STARTUP SEQUENCE ---
# 1. Start Airflow in 'standalone' mode (handles DB init and user creation automatically)
# 2. Wait 5 seconds to ensure system resources are allocated
# 3. Start FastAPI using the package path (app.main:app)
CMD ["sh", "-c", "airflow standalone & sleep 5 && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"]
