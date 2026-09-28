import os
import json
import pickle
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

def train_models():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    data_path = os.path.join(base_dir, "data", "Crop_recommendation.csv")
    models_dir = os.path.join(base_dir, "models")
    os.makedirs(models_dir, exist_ok=True)
    
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Dataset not found at {data_path}. Please run download_data.py first.")
        
    print("Loading dataset...")
    df = pd.read_csv(data_path)
    
    # Basic data info
    print(f"Dataset shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    
    # Preprocessing: Check for missing values
    missing_values = df.isnull().sum().sum()
    if missing_values > 0:
        print(f"Found {missing_values} missing values. Handling them by dropping rows.")
        df = df.dropna()
    else:
        print("No missing values found in the dataset.")
        
    # Split into features and target
    X = df.drop('label', axis=1)
    y = df['label']
    
    # Split into train and test sets (80% train, 20% test)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    print(f"Training set shape: {X_train.shape}, Test set shape: {X_test.shape}")
    
    # 1. Train Decision Tree
    print("Training Decision Tree Classifier...")
    dt_model = DecisionTreeClassifier(random_state=42)
    dt_model.fit(X_train, y_train)
    
    # 2. Train Random Forest
    print("Training Random Forest Classifier...")
    rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
    rf_model.fit(X_train, y_train)
    
    
    # Evaluate Decision Tree
    dt_pred = dt_model.predict(X_test)
    dt_acc = accuracy_score(y_test, dt_pred)
    dt_precision, dt_recall, dt_f1, _ = precision_recall_fscore_support(y_test, dt_pred, average='weighted')
    
    # Evaluate Random Forest
    rf_pred = rf_model.predict(X_test)
    rf_acc = accuracy_score(y_test, rf_pred)
    rf_precision, rf_recall, rf_f1, _ = precision_recall_fscore_support(y_test, rf_pred, average='weighted')
    
    print("\nModel Evaluation Results:")
    print("=" * 45)
    print(f"Decision Tree  - Accuracy: {dt_acc:.4f}, Precision: {dt_precision:.4f}, Recall: {dt_recall:.4f}, F1: {dt_f1:.4f}")
    print(f"Random Forest  - Accuracy: {rf_acc:.4f}, Precision: {rf_precision:.4f}, Recall: {rf_recall:.4f}, F1: {rf_f1:.4f}")
    print("=" * 45)
    
    # Feature Importance (Random Forest)
    importances = rf_model.feature_importances_
    features = list(X.columns)
    feature_importance = [{"feature": f, "importance": float(imp)} for f, imp in zip(features, importances)]
    feature_importance = sorted(feature_importance, key=lambda x: x["importance"], reverse=True)
    
    print("\nFeature Importances (Random Forest):")
    for f in feature_importance:
        print(f"  {f['feature']}: {f['importance']:.4f}")
        
    # Serialize Models
    dt_path = os.path.join(models_dir, "decision_tree_model.pkl")
    rf_path = os.path.join(models_dir, "random_forest_model.pkl")
    
    with open(dt_path, 'wb') as f:
        pickle.dump(dt_model, f)
    with open(rf_path, 'wb') as f:
        pickle.dump(rf_model, f)
        
    print(f"\nModels saved to:\n  - {dt_path}\n  - {rf_path}")
    
    # Save Metrics
    metrics = {
        "decision_tree": {
            "accuracy": float(dt_acc),
            "precision": float(dt_precision),
            "recall": float(dt_recall),
            "f1_score": float(dt_f1)
        },
        "random_forest": {
            "accuracy": float(rf_acc),
            "precision": float(rf_precision),
            "recall": float(rf_recall),
            "f1_score": float(rf_f1)
        },
        "feature_importances": feature_importance,
        "classes": list(rf_model.classes_)
    }
    
    metrics_path = os.path.join(models_dir, "metrics.json")
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f, indent=4)
    print(f"Metrics saved to: {metrics_path}")

if __name__ == "__main__":
    train_models()
