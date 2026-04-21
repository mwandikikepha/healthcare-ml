import os
import pandas as pd
from dotenv import load_dotenv
from database.db_connection import get_engine
from scripts.clean import clean_data 

load_dotenv()

def load_to_postgres():
    engine = get_engine()
    print(" Starting data loading process...")
    
    try:
        # 1. Extract Raw Data
        raw_df = pd.read_sql("SELECT * FROM raw_healthcare_data", engine)
        
        # 2. Transform (The Clean Step)
        cleaned_df = clean_data(raw_df)
        
        # 3. Load to Database
        cleaned_df.to_sql('cleaned_healthcare_data', engine, if_exists='append', index=False)
        print(f"Successfully loaded {len(cleaned_df)} rows to 'cleaned_healthcare_data'.")
        
        # 4. Save Local Backup (CSV)
        save_path = os.getenv('save_path')
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        cleaned_df.to_csv(save_path, index=False)
        print(f"Cleaned data saved locally to: {save_path}")
        
    except Exception as e:
        print(f"Error during load process: {e}")

if __name__ == "__main__":
    load_to_postgres()