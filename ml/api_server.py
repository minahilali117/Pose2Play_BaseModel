from flask import Flask, request, jsonify
from flask_cors import CORS
from stable_baselines3 import DQN
import numpy as np
import os
from pathlib import Path
import sys

# Add ml directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from form_feedback import FormFeedbackGenerator

app = Flask(__name__)
CORS(app)

# Load RL model for difficulty adjustment
model_path = './models/dqn/DQN_rehab_final.zip'
if os.path.exists(model_path):
    model = DQN.load(model_path)
    print(f"✅ Loaded RL model: {model_path}")
else:
    print(f"⚠️ RL model not found: {model_path}")
    model = None

# Load form classification model
form_model_path = './models/form_classifier/form_classifier_rf.pkl'
if os.path.exists(form_model_path):
    form_classifier = FormFeedbackGenerator(form_model_path)
    print(f"✅ Loaded form classifier: {form_model_path}")
else:
    print(f"⚠️ Form classifier not found: {form_model_path}")
    form_classifier = None

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok', 
        'rl_model_loaded': model is not None,
        'form_classifier_loaded': form_classifier is not None
    })

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        state = np.array(data['state'], dtype=np.float32)
        
        if model is None:
            return jsonify({'error': 'Model not loaded'}), 500
        
        # Get action from trained model
        action, _ = model.predict(state, deterministic=True)
        
        # Map action to description
        action_names = ['decrease_difficulty', 'maintain', 'increase_difficulty', 'rest_break', 'encouragement']
        action_name = action_names[int(action)]
        
        return jsonify({
            'action': int(action),
            'action_name': action_name,
            'confidence': float(0.95)  # Placeholder
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/predict_form', methods=['POST'])
def predict_form():
    """
    Predict exercise form quality and provide corrections
    
    Expected input:
    {
        "features": [59-element array of sensor features],
        "exercise_type": "squat" | "hip_abduction_left" | etc.
    }
    
    Returns:
    {
        "prediction": 0 or 1,
        "form_quality": "87.5%",
        "is_correct": true/false,
        "feedback": ["Great depth!", ...],
        "corrections": ["Keep knees aligned", ...],
        "issues_detected": ["knee_valgus", ...]
    }
    """
    try:
        if form_classifier is None:
            return jsonify({'error': 'Form classifier not loaded'}), 500
        
        data = request.json
        features = np.array(data.get('features', []), dtype=np.float32)
        exercise_type = data.get('exercise_type', 'squat')
        
        if len(features) == 0:
            return jsonify({'error': 'No features provided'}), 400
        
        # Analyze form
        result = form_classifier.analyze_form(features, exercise_type)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/predict_form_simple', methods=['POST'])
def predict_form_simple():
    """
    Simplified form prediction for webcam-based exercises
    Uses simplified feature extraction from pose landmarks
    
    Expected input:
    {
        "angles": {
            "knee_left": 85,
            "knee_right": 87,
            "hip_left": 90,
            "hip_right": 88
        },
        "movement_speed": 2.5,  # seconds per rep
        "exercise_type": "squat"
    }
    
    Returns: Same as /predict_form but with rule-based analysis
    """
    try:
        data = request.json
        angles = data.get('angles', {})
        movement_speed = data.get('movement_speed', 3.0)
        exercise_type = data.get('exercise_type', 'squat')
        
        # Simple rule-based form analysis for webcam exercises
        feedback = []
        corrections = []
        issues = []
        is_correct = True
        form_quality = 100.0
        
        if exercise_type == 'squat':
            knee_left = angles.get('knee_left', 90)
            knee_right = angles.get('knee_right', 90)
            
            # Check depth
            avg_knee = (knee_left + knee_right) / 2
            if avg_knee > 100:
                issues.append('shallow_depth')
                corrections.append("⚠️ Squat deeper - aim for 90° or below")
                form_quality -= 20
                is_correct = False
            
            # Check asymmetry
            asymmetry = abs(knee_left - knee_right)
            if asymmetry > 10:
                issues.append('asymmetry')
                corrections.append(f"⚠️ Uneven depth - left: {knee_left:.0f}°, right: {knee_right:.0f}°")
                form_quality -= 15
                is_correct = False
            
            # Check speed
            if movement_speed < 1.5:
                issues.append('too_fast')
                corrections.append("⚠️ Slow down - take 2-3 seconds per rep")
                form_quality -= 10
                is_correct = False
            
            # Positive feedback if form is good
            if is_correct:
                feedback.append("✅ Excellent form! Perfect depth and balance.")
        
        elif 'hip' in exercise_type:
            hip_angle = angles.get('hip_left' if 'left' in exercise_type else 'hip_right', 90)
            
            # Check range
            if hip_angle > 120:
                issues.append('insufficient_lift')
                corrections.append("⚠️ Lift leg higher - aim for 45°")
                form_quality -= 25
                is_correct = False
            
            if is_correct:
                feedback.append("✅ Perfect! Good range of motion.")
        
        elif 'shoulder' in exercise_type:
            shoulder_angle = angles.get('shoulder_left', 90)
            
            # Check range
            if shoulder_angle < 80:
                issues.append('insufficient_raise')
                corrections.append("⚠️ Raise arm higher - aim for 90°")
                form_quality -= 20
                is_correct = False
            
            if is_correct:
                feedback.append("✅ Great! Arm at perfect height.")
        
        # If no specific feedback, add generic
        if not feedback and not corrections:
            if is_correct:
                feedback.append("✅ Good form! Keep it up.")
            else:
                corrections.append("⚠️ Form needs improvement")
        
        form_quality = max(0, form_quality)
        
        return jsonify({
            'prediction': 1 if is_correct else 0,
            'form_quality': f"{form_quality:.1f}%",
            'is_correct': is_correct,
            'feedback': feedback,
            'corrections': corrections,
            'issues': issues,  # Keep both for compatibility
            'issues_detected': issues,
            'confidence': form_quality / 100.0
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    print("🚀 RL API Server Starting...")
    print("Available endpoints:")
    print("  GET  /health              - Check server status")
    print("  POST /predict             - Get RL difficulty adjustment action")
    print("  POST /predict_form        - Analyze form with ML classifier (sensor data)")
    print("  POST /predict_form_simple - Analyze form with rules (webcam angles)")
    print("\nListening on http://localhost:5000")
    app.run(host='localhost', port=5000, debug=True)
