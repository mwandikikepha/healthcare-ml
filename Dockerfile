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

# Uninstall any potential SQLAlchemy 2.0 and force 1.4.x
RUN uv pip install --system "sqlalchemy<2.0" --force-reinstall

# Install everything else
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


# preventing a "Deploy-Crash-Loop"
RUN ls -la /app/models/final_model.joblib

ENV AIRFLOW_HOME=/app/airflow_home
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

EXPOSE 8000 8080

# We only run the scheduler and webserver, skipping the triggerer to save RAM
CMD ["sh", "-c", "airflow db migrate && (airflow webserver --port 8080 & airflow scheduler & python -m uvicorn app.main:app --host 0.0.0.0 --port 8000)"]
