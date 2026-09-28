import os
import pickle
import json
import numpy as np

class CropPredictor:
    def __init__(self):
        base_dir = os.path.dirname(os.path.dirname(__file__))
        models_dir = os.path.join(base_dir, "models")
        
        self.rf_model_path = os.path.join(models_dir, "random_forest_model.pkl")
        self.metrics_path = os.path.join(models_dir, "metrics.json")
        
        self.model = None
        self.classes = []
        self.feature_names = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
        
        self.load_model()
        
    def load_model(self):
        if not os.path.exists(self.rf_model_path) or not os.path.exists(self.metrics_path):
            raise FileNotFoundError("Trained model or metrics file not found. Run train.py first.")
            
        with open(self.rf_model_path, 'rb') as f:
            self.model = pickle.load(f)
            
        with open(self.metrics_path, 'r') as f:
            metrics = json.load(f)
            self.classes = metrics.get('classes', [])
            
    def predict(self, n, p, k, temp, humidity, ph, rainfall):
        if self.model is None:
            self.load_model()
            
        # Structure input features as DataFrame to preserve feature names
        import pandas as pd
        input_data = pd.DataFrame([[n, p, k, temp, humidity, ph, rainfall]], columns=self.feature_names)
        
        # Predict the crop class
        prediction = self.model.predict(input_data)[0]
        
        # Get probability distribution
        probabilities = self.model.predict_proba(input_data)[0]
        
        # Zip classes with their probabilities and sort by confidence descending
        prob_dict = {cls: float(prob) for cls, prob in zip(self.classes, probabilities)}
        sorted_probs = sorted(prob_dict.items(), key=lambda x: x[1], reverse=True)
        
        # Filter classes with confidence > 0.01 for cleaner visualization
        top_recommendations = [{"crop": crop, "confidence": prob} for crop, prob in sorted_probs if prob > 0.005]
        
        return {
            "prediction": prediction,
            "confidence": prob_dict.get(prediction, 0.0),
            "recommendations": top_recommendations
        }

if __name__ == "__main__":
    # Quick sanity test
    try:
        predictor = CropPredictor()
        # Test input matching Rice (N=90, P=42, K=43, Temp=21, Humidity=82, pH=6.5, Rainfall=203)
        res = predictor.predict(90, 42, 43, 21.0, 82.0, 6.5, 203.0)
        print("Test prediction result:", res)
    except Exception as e:
        print("Prediction test failed (models might not be trained yet):", e)
