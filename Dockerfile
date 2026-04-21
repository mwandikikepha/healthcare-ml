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

# Use --system so uv doesn't look for a .venv
RUN uv pip install --system "fastapi[standard]" "apache-airflow==2.10.2" "psycopg2-binary"

# 2. Sync the rest of your project dependencies
RUN uv sync --system

# Set environment variables
ENV AIRFLOW_HOME=/app/airflow_home
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose ports
EXPOSE 8000 8080

# --- THE START COMMAND ---
# Now we can call the binaries directly because they are in the system PATH
CMD ["sh", "-c", "airflow standalone & fastapi run web/app.py --port 8000"]
