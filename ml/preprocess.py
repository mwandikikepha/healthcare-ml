import pandas as pd
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder, LabelEncoder
from database.db_connection import get_engine

def preprocess_data():
    engine = get_engine()
    print(" Loading cleaned data from Postgres...")
    df = pd.read_sql("SELECT * FROM cleaned_healthcare_data", engine)

    # Drop the SQL ID
    if 'id' in df.columns:
        df = df.drop(columns=['id'])

    # Target Encoding (y)
    le = LabelEncoder()
    y = le.fit_transform(df['test_results'])
    X = df.drop(columns=['test_results'])

    #  Identify Column Types
    cat_cols = X.select_dtypes(include=['object']).columns.tolist()
    num_cols = X.select_dtypes(include=['int64', 'float64']).columns.tolist()

    # Feature Encoding (X)
    # handle_unknown='ignore' 
    ohe = OneHotEncoder(handle_unknown='ignore', sparse_output=False)
    X_encoded_cats = ohe.fit_transform(X[cat_cols])
    cat_feature_names = ohe.get_feature_names_out(cat_cols)
    
    #  Scaling Numerical Features
    scaler = StandardScaler()
    X_scaled_nums = scaler.fit_transform(X[num_cols])

    #Reconstruct the DataFrame
    X_final = pd.concat([
        pd.DataFrame(X_scaled_nums, columns=num_cols),
        pd.DataFrame(X_encoded_cats, columns=cat_feature_names)
    ], axis=1)

    #  Train/Test Split
    X_train, X_test, y_train, y_test = train_test_split(
        X_final, y, test_size=0.2, random_state=42, stratify=y
    )

    #  Save Everything
    os.makedirs('models', exist_ok=True)
    os.makedirs('data/processed', exist_ok=True)
    
    # Save the math objects for the API
    joblib.dump(le, 'models/label_encoder.joblib')
    joblib.dump(ohe, 'models/onehot_encoder.joblib')
    joblib.dump(scaler, 'models/scaler.joblib')
    
    # Save the processed data for the training script
    X_train.to_csv('data/processed/X_train.csv', index=False)
    X_test.to_csv('data/processed/X_test.csv', index=False)
    pd.Series(y_train).to_csv('data/processed/y_train.csv', index=False)
    pd.Series(y_test).to_csv('data/processed/y_test.csv', index=False)

    print(f" Preprocessing complete! Feature count: {X_final.shape[1]}")
    print("Objects saved in /models and processed data in /data/processed")

if __name__ == "__main__":
    preprocess_data()
