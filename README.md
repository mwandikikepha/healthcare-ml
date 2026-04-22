# Healthcare ML Pipeline

> End-to-end machine learning system that ingests synthetic healthcare data, stores it in PostgreSQL, retrains a classification model every Saturday at noon, and serves live predictions via a FastAPI endpoint.

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![XGBoost](https://img.shields.io/badge/XGBoost-2.x-FF6600?style=flat-square)](https://xgboost.readthedocs.io/)
[![Airflow](https://img.shields.io/badge/Apache%20Airflow-2.x-017CEE?style=flat-square&logo=apacheairflow&logoColor=white)](https://airflow.apache.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=flat-square&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?style=flat-square&logo=docker&logoColor=white)](https://www.docker.com/)
[![Railway](https://img.shields.io/badge/Deployed%20on-Railway-0B0D0E?style=flat-square&logo=railway)](https://railway.app/)

**Live API:** [https://healthcare-ml-production.up.railway.app](https://healthcare-ml-production.up.railway.app)  
**Docs:** [https://healthcare-ml-production.up.railway.app/docs](https://healthcare-ml-production.up.railway.app/docs)

---

## What It Does

The system has three responsibilities:

1. **Data pipeline** — Downloads 10,000 synthetic healthcare records from Kaggle, cleans and validates them, then loads the data into a PostgreSQL database with duplicate prevention.
2. **Scheduled retraining** — An Apache Airflow DAG triggers every Saturday at 12:00 noon. It pulls the latest data from the database, preprocesses features, trains an XGBoost classifier (with a Logistic Regression baseline for comparison), evaluates both models, and saves the best-performing one.
3. **Prediction API** — A FastAPI service loads the saved model and exposes a `/predict` endpoint. Send a patient record, receive a predicted test result: `Normal`, `Abnormal`, or `Inconclusive`.

---

## Project Structure

```
healthcare-ml/
├── airflow/
│   └── dags/
│       └── healthcare_ml_dag.py   # Weekly retraining DAG (Saturday 12:00)
├── app/
│   ├── main.py                    # FastAPI app entry point
│   ├── routes.py                  # /predict and health check routes
│   ├── schemas.py                 # Pydantic request/response models
│   ├── model_loader.py            # Loads joblib artifacts at startup
│   └── utils.py                   # Shared helpers
├── database/
│   ├── db_connection.py           # SQLAlchemy engine setup
│   ├── models.py                  # ORM table definitions
│   └── queries.sql                # Reference SQL
├── ml/
│   ├── preprocess.py              # Feature engineering pipeline
│   ├── train.py                   # Model training (XGBoost + LR)
│   ├── evaluate.py                # Metrics: accuracy, precision, recall, F1, confusion matrix
│   └── predict.py                 # Inference helper
├── scripts/
│   ├── ingest.py                  # Download and store raw data
│   ├── clean.py                   # Cleaning and transformation
│   └── load.py                    # Load cleaned data into PostgreSQL
├── models/                        # Saved joblib artifacts
│   ├── final_model.joblib
│   ├── label_encoder.joblib
│   ├── onehot_encoder.joblib
│   └── scaler.joblib
├── data/
│   ├── cleaned_healthcare.csv
│   ├── raw/healthcare_raw_backup.csv
│   └── processed/                 # Train/test splits
├── frontend/index.html            # Simple test UI
├── notebooks/analysis.ipynb      # EDA
├── tests/test_api.py
├── Dockerfile
├── docker-compose.yml
└── pyproject.toml
```

---

## Dataset

**Source:** [Kaggle — Healthcare Dataset](https://www.kaggle.com/datasets/prasad22/healthcare-dataset/data) by Prasad (10,000 synthetic patient records)

| Column | Description |
|---|---|
| Age | Patient age |
| Gender | Male / Female |
| Blood Type | ABO + Rh group |
| Medical Condition | Primary diagnosis |
| Date of Admission | Admission timestamp |
| Discharge Date | Discharge timestamp |
| Billing Amount | Total billed (USD) |
| Admission Type | Emergency / Elective / Urgent |
| Insurance Provider | Payer name |
| Medication | Prescribed drug |
| Test Results | **Target** — Normal / Abnormal / Inconclusive |

**Derived feature:** `Days_Hospitalized` (discharge − admission) is engineered during preprocessing.

---

## Machine Learning

### Preprocessing
- Missing values imputed (median for numerics, mode for categoricals)
- `Date of Admission` and `Discharge Date` parsed and converted to derive `Days_Hospitalized`
- Categorical features encoded with `OneHotEncoder` (no ordinal assumptions)
- Numeric features (`Age`, `Billing Amount`, `Days_Hospitalized`) scaled with `StandardScaler`
- Target encoded with `LabelEncoder` → {0: Abnormal, 1: Inconclusive, 2: Normal}

### Models Trained
| Model | Role |
|---|---|
| XGBoost (`multi:softprob`) | Primary classifier |
| Logistic Regression | Baseline comparison |

### Evaluation Metrics
Every training run produces:
- Accuracy, Precision, Recall, F1-score (weighted)
- Per-class breakdown
- Confusion matrix

### Retraining Schedule
The Airflow DAG `healthcare_ml_pipeline` runs on a `cron` of `0 12 * * 6` (every Saturday at noon). Tasks in order:

```
extract_from_db → preprocess → train_models → evaluate → save_best_model
```

---

## API Reference

### `GET /`
Health check.

```json
{ "status": "ok", "message": "Healthcare ML API is running" }
```

### `POST /predict`

**Request:**
```json
{
  "Age": 45,
  "Gender": "Male",
  "Blood Type": "O+",
  "Medical Condition": "Diabetes",
  "Billing Amount": 2000.50,
  "Admission Type": "Emergency",
  "Insurance Provider": "Cigna",
  "Medication": "Aspirin"
}
```

**Response:**
```json
{
  "predicted_test_result": "Abnormal"
}
```

**Try it live:**
```bash
curl -X POST https://healthcare-ml-production.up.railway.app/predict \
  -H "Content-Type: application/json" \
  -d '{
    "Age": 45,
    "Gender": "Male",
    "Blood Type": "O+",
    "Medical Condition": "Diabetes",
    "Billing Amount": 2000.50,
    "Admission Type": "Emergency",
    "Insurance Provider": "Cigna",
    "Medication": "Aspirin"
  }'
```

Interactive docs available at [`/docs`](https://healthcare-ml-production.up.railway.app/docs).

---

## Local Setup

### Prerequisites
- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (package manager)
- PostgreSQL 14+ running locally or via Docker
- Docker & Docker Compose (optional but recommended)

### 1. Clone and install dependencies

```bash
git clone https://github.com/mwandikikepha/healthcare-ml.git
cd healthcare-ml
uv sync
```

### 2. Configure environment

Create a `.env` file at the project root:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/healthcare_db
KAGGLE_USERNAME=your_kaggle_username
KAGGLE_KEY=your_kaggle_api_key
```

Set up Kaggle credentials by following the [Kaggle API docs](https://www.kaggle.com/docs/api#authentication).

### 3. Set up the database

```bash
uv run python db_setup.py
```

### 4. Ingest and clean data

```bash
uv run python scripts/ingest.py    # Download from Kaggle and store raw backup
uv run python scripts/clean.py     # Clean and transform
uv run python scripts/load.py      # Load into PostgreSQL
```

### 5. Train the model (one-off)

```bash
uv run python ml/train.py
```

### 6. Start the API

```bash
uv run uvicorn app.main:app --reload --port 8000
```

The API will be live at `http://localhost:8000`. Docs at `http://localhost:8000/docs`.

---

## Docker

### Run with Docker Compose (API + PostgreSQL)

```bash
docker-compose up --build
```

This starts:
- **PostgreSQL** on port `5432`
- **FastAPI** on port `8000`
- **Airflow** scheduler (standalone mode) on port `8080`

### Build and run manually

```bash
docker build -t healthcare-predictor .
docker run -p 8000:8000 --env-file .env healthcare-predictor
```

---

## Running Tests

```bash
uv run pytest tests/
```

`tests/test_api.py` covers the `/predict` endpoint with valid and invalid payloads.

---

## Deployment (Railway)

This project is deployed on [Railway](https://railway.app/) with a PostgreSQL plugin attached.

To deploy your own instance:

1. Fork this repository
2. Create a new Railway project and connect your GitHub repo
3. Add a PostgreSQL plugin from the Railway dashboard
4. Set the following environment variables in Railway:
   - `DATABASE_URL` (auto-filled by Railway's PostgreSQL plugin)
   - `KAGGLE_USERNAME`
   - `KAGGLE_KEY`
5. Railway will build from the `Dockerfile` and deploy automatically on each push to `main`

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12 |
| API Framework | FastAPI + Uvicorn |
| ML Models | XGBoost, Scikit-learn |
| Orchestration | Apache Airflow |
| Database | PostgreSQL + SQLAlchemy |
| Containerization | Docker + Docker Compose |
| Package Manager | uv |
| Model Serialization | joblib |
| Deployment | Railway |

---

## Author

**Kepha Mwandiki**  
Data Engineer & Data Scientist  
GitHub: [@mwandikikepha](https://github.com/mwandikikepha)

---

*Built as part of the LuxDevHQ May/June Pre-Internship Project.*
