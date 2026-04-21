FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy project files
COPY . .

# --- THE STRICT INSTALL ---
# 1. Uninstall any potential SQLAlchemy 2.0 and force 1.4.x
RUN uv pip install --system "sqlalchemy<2.0" --force-reinstall

# 2. Install everything else
RUN uv pip install --system \
    "fastapi[standard]" \
    "apache-airflow==2.10.2" \
    "psycopg2-binary" \
    "xgboost" \
    "joblib" \
    "uvicorn" \
    "pandas" \
    "numpy" \
    "scikit-learn"

# --- THE CRITICAL SAFETY CHECK ---
# This will make the build FAIL in Railway if the model isn't there, 
# preventing a "Deploy-Crash-Loop"
RUN ls -la /app/models/final_model.joblib

ENV AIRFLOW_HOME=/app/airflow_home
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

EXPOSE 8000 8080

CMD ["sh", "-c", "airflow standalone & sleep 15 && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"]
CMD ["sh", "-c", "airflow standalone & sleep 5 && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"]
