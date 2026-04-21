# Use a slim Python 3.12 image
FROM python:3.12-slim

# Install system dependencies for Postgres, SSL (for Aiven), and Airflow
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Install 'uv' from the official binary
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy your project files into the container
COPY . .

# Install dependencies using uv
# (This assumes you have a pyproject.toml or requirements.txt)
RUN uv sync

# Set critical environment variables
ENV AIRFLOW_HOME=/app/airflow_home
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose ports for FastAPI (8000) and Airflow (8080)
EXPOSE 8000 8080

# Initialize Airflow DB and start both services
# We use 'standalone' for Airflow to simplify process management in a single container
CMD ["sh", "-c", "uv run airflow standalone & uv run fastapi run web/app.py --port 8000"]