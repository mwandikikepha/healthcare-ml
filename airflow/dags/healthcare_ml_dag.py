from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
import os
import sys

# HELP AIRFLOW FIND YOUR PROJECT
# This allows Airflow to "see" your scripts and ml folders
PROJECT_ROOT = os.getenv('PYTHONPATH', '/app')
sys.path.append(PROJECT_ROOT)

default_args = {
    'owner': 'kepha',
    'depends_on_past': False,
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'healthcare_ml_pipeline',
    default_args=default_args,
    description='End-to-end Healthcare ML Pipeline',
    schedule='@weekly',
    start_date=datetime(2026, 1, 1),
    catchup=False,
) as dag:

    # Task 1: Ingest
    # We use "cd" to the root so your scripts can find the /data folder
    ingest_data = BashOperator(
        task_id='ingest_data',
        bash_command=f'cd {PROJECT_ROOT} && uv run python scripts/ingest.py',
    )

    # Task 2: Clean
    clean_data = BashOperator(
        task_id='clean_data',
        bash_command=f'cd {PROJECT_ROOT} && uv run python scripts/clean.py',
    )

    # Task 3: Preprocess
    preprocess_data = BashOperator(
        task_id='preprocess_data',
        bash_command=f'cd {PROJECT_ROOT} && uv run python ml/preprocess.py',
    )

    # Task 4: Train
    train_model = BashOperator(
        task_id='train_model',
        bash_command=f'cd {PROJECT_ROOT} && uv run python ml/train.py',
    )

    ingest_data >> clean_data >> preprocess_data >> train_model
