import pandas as pd

def clean_data(df):
    print(" Transforming data...")
    
    # 1. Handle Dates & Length of Stay
    df['Date of Admission'] = pd.to_datetime(df['Date of Admission'])
    df['Discharge Date'] = pd.to_datetime(df['Discharge Date'])
    df['days_hospitalized'] = (df['Discharge Date'] - df['Date of Admission']).dt.days
    
    # 2. Fix Billing
    df['billing_amount'] = df['Billing Amount'].abs()

    # 3. Select and Rename Features
    keep_columns = {
        'Age': 'age',
        'Gender': 'gender',
        'Blood Type': 'blood_type',
        'Medical Condition': 'medical_condition',
        'Insurance Provider': 'insurance_provider',
        'Admission Type': 'admission_type',
        'Medication': 'medication',
        'Test Results': 'test_results'
    }

    cleaned_df = df[list(keep_columns.keys())].copy()
    cleaned_df.rename(columns=keep_columns, inplace=True)
    
    cleaned_df['days_hospitalized'] = df['days_hospitalized']
    cleaned_df['billing_amount'] = df['billing_amount']

    # 4. Standardize Text
    for col in cleaned_df.select_dtypes(include=['object']):
        cleaned_df[col] = cleaned_df[col].str.lower().str.strip()

    return cleaned_df