import os
import json
from flask import Flask, request, jsonify, send_from_directory
from predict import CropPredictor

# Initialize Flask app
# Since app.py is in src/, static folder is one level up in 'static'
base_dir = os.path.dirname(os.path.dirname(__file__))
static_dir = os.path.join(base_dir, "static")

app = Flask(__name__, static_folder=static_dir, static_url_path="")

# Initialize predictor lazily
predictor = None

def get_predictor():
    global predictor
    if predictor is None:
        predictor = CropPredictor()
    return predictor

@app.route('/')
def home():
    return app.send_static_file('index.html')

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    metrics_path = os.path.join(base_dir, "models", "metrics.json")
    if not os.path.exists(metrics_path):
        return jsonify({"error": "Models are not trained yet. Please run training first."}), 400
        
    try:
        with open(metrics_path, 'r') as f:
            metrics = json.load(f)
        return jsonify(metrics)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid request payload. Expected JSON."}), 400
            
        required_fields = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
        inputs = {}
        
        # Validation and parsing
        for field in required_fields:
            if field not in data or data[field] is None:
                return jsonify({"error": f"Missing required parameter: {field}"}), 400
            try:
                inputs[field] = float(data[field])
            except ValueError:
                return jsonify({"error": f"Parameter {field} must be a number."}), 400
                
        # Value ranges checks
        if inputs['ph'] < 0 or inputs['ph'] > 14:
            return jsonify({"error": "pH value must be between 0 and 14."}), 400
        if inputs['humidity'] < 0 or inputs['humidity'] > 100:
            return jsonify({"error": "Humidity must be between 0% and 100%."}), 400
        if inputs['rainfall'] < 0:
            return jsonify({"error": "Rainfall cannot be negative."}), 400
        if inputs['N'] < 0 or inputs['P'] < 0 or inputs['K'] < 0:
            return jsonify({"error": "Soil nutrients (N, P, K) cannot be negative."}), 400
            
        # Get prediction
        pred_engine = get_predictor()
        result = pred_engine.predict(
            n=inputs['N'],
            p=inputs['P'],
            k=inputs['K'],
            temp=inputs['temperature'],
            humidity=inputs['humidity'],
            ph=inputs['ph'],
            rainfall=inputs['rainfall']
        )
        
        return jsonify({
            "status": "success",
            "input": inputs,
            "prediction": result["prediction"],
            "confidence": result["confidence"],
            "recommendations": result["recommendations"]
        })
        
    except FileNotFoundError:
        return jsonify({"error": "Models are not trained yet. Please run training first."}), 400
    except Exception as e:
        return jsonify({"error": f"Prediction failed: {str(e)}"}), 500

# Catch-all to serve static files correctly
@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(static_dir, path)

if __name__ == '__main__':
    # Try loading the predictor once at startup to warm up
    try:
        get_predictor()
        print("Model loaded successfully.")
    except Exception as e:
        print("Warning: Model could not be loaded at startup. It will load on first request or after training. Error:", e)
        
    print("Starting crop recommendation server on http://127.0.0.1:5000")
    app.run(debug=True, host='127.0.0.1', port=5000)
