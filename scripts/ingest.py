import os
import kagglehub
import pandas as pd
from database.db_connection import get_engine

def ingest_data():
    print("Starting Data Ingestion...")
    
    
    try:
        path = kagglehub.dataset_download("prasad22/healthcare-dataset")
        csv_path = os.path.join(path, "healthcare_dataset.csv")
        print(f"Data downloaded to: {csv_path}")
    except Exception as e:
        print(f"Failed to download dataset: {e}")
        return

    # 2. Load into Pandas
    df = pd.read_csv(csv_path)
    
    # 3. Store Raw Copy in PostgreSQL
    # We use 'replace' for the raw table to keep it as a fresh snapshot
    try:
        engine = get_engine()
        df.to_sql('raw_healthcare_data', engine, if_exists='replace', index=False)
        print(f"Successfully loaded {len(df)} records into 'raw_healthcare_data' table.")
        
        # Also save a local backup in your data/raw folder
        df.to_csv('data/raw/healthcare_raw_backup.csv', index=False)
        
    except Exception as e:
        print(f" Database error: {e}")

if __name__ == "__main__":
    ingest_data()