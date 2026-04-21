from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import pandas as pd
import numpy as np
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

# 1. Initialize FastAPI
app = FastAPI(title="Healthcare Test Result Predictor")



# Look for /app first (Docker), then fallback to local relative path
if os.path.isdir('/app/models'):
    BASE_DIR = '/app'
else:
    # Gets the root by going up from app/main.py
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def load_artifact(filename):
    path = os.path.join(BASE_DIR, 'models', filename)
    print(f"DEBUG: Loading from {path}")
    return joblib.load(path)

# Ensure these all load from the same BASE_DIR
model = load_artifact('final_model.joblib')
ohe = load_artifact('onehot_encoder.joblib')
scaler = load_artifact('scaler.joblib')
le = load_artifact('label_encoder.joblib')

# 3. Define the Request Structure (Pydantic)
class PatientData(BaseModel):
    Age: int
    Gender: str
    Blood_Type: str
    Medical_Condition: str
    Insurance_Provider: str
    Admission_Type: str
    Medication: str
    Days_Hospitalized: int
    Billing_Amount: float

# 4. Routes

@app.get("/")
def home():
    """Serves the Web UI at the root address."""
    return FileResponse(os.path.join("frontend", "index.html"))

@app.get("/ui")
def read_index():
    """Alternative route for the UI."""
    return FileResponse(os.path.join("frontend", "index.html"))

@app.post("/predict")
def predict(data: PatientData):
    """The Machine Learning Inference Endpoint."""
    try:
        # Convert input to DataFrame
        input_dict = data.model_dump()
        input_df = pd.DataFrame([input_dict])

        # Standardize column names and casing to match our training pipeline
        input_df.columns = [c.lower() for c in input_df.columns]
        for col in input_df.select_dtypes(include=['object']):
            input_df[col] = input_df[col].str.lower().str.strip()

        # Define column groups
        cat_cols = ['gender', 'blood_type', 'medical_condition', 'insurance_provider', 'admission_type', 'medication']
        num_cols = ['age', 'days_hospitalized', 'billing_amount']

        # Apply the pre-trained transformations
        X_cat = ohe.transform(input_df[cat_cols])
        X_num = scaler.transform(input_df[num_cols])
        
        # Combine numerical and categorical features
        X_final = np.hstack([X_num, X_cat])

        # Make Prediction using XGBoost
        pred_idx = model.predict(X_final)[0]
        prediction = le.inverse_transform([pred_idx])[0]
        
        # Calculate Probability
        prob = model.predict_proba(X_final).max()

        return {
            "test_result_prediction": prediction,
            "confidence_score": f"{prob:.2%}"
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# 5. Static Files (Mounting the frontend folder for CSS/JS access)
app.mount("/static", StaticFiles(directory="frontend"), name="static")
