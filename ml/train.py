import pandas as pd
import joblib
import os
from xgboost import XGBClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report

def train_models():
    print("Starting the Model Training...")
    
    # 1. Load the processed data
    X_train = pd.read_csv('data/processed/X_train.csv')
    X_test = pd.read_csv('data/processed/X_test.csv')
    y_train = pd.read_csv('data/processed/y_train.csv').values.ravel()
    y_test = pd.read_csv('data/processed/y_test.csv').values.ravel()

    # 2. Define the candidates
    models = {
        "Logistic_Regression": LogisticRegression(max_iter=1000, random_state=42),
        "XGBoost": XGBClassifier(use_label_encoder=False, eval_metric='mlogloss', random_state=42)
    }

    best_model = None
    best_accuracy = 0
    results = {}

    # 3. Training and Evaluation loop
    for name, model in models.items():
        print(f"Training {name}...")
        model.fit(X_train, y_train)
        
        predictions = model.predict(X_test)
        acc = accuracy_score(y_test, predictions)
        results[name] = acc
        
        print(f" {name} Accuracy: {acc:.4f}")
        
        if acc > best_accuracy:
            best_accuracy = acc
            best_model = model
            best_name = name

    # 4. Save the Champion
    print(f"\nThe Winner is: {best_name} with {best_accuracy:.4f} accuracy!")
    
    os.makedirs('models', exist_ok=True)
    joblib.dump(best_model, 'models/final_model.joblib')
    
    # Optional: Print a detailed report for the winner
    final_preds = best_model.predict(X_test)
    print("\nDetailed Performance Report:")
    print(classification_report(y_test, final_preds))

if __name__ == "__main__":
    train_models()