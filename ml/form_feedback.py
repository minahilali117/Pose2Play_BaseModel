"""
Form Feedback Generator
Analyzes exercise performance and provides specific corrections

Uses feature importance and thresholds to identify form issues
"""

import numpy as np
import joblib
from pathlib import Path
from typing import Dict, List

class FormFeedbackGenerator:
    """Generate specific form corrections based on sensor data"""
    
    # Form issue detection thresholds (learned from data)
    THRESHOLDS = {
        # Acceleration thresholds (g-forces)
        'accel_x_max': 2.5,
        'accel_y_max': 2.5,
        'accel_z_max': 12.0,  # Vertical should be ~9.81 at rest
        
        # Gyroscope thresholds (deg/sec)
        'gyro_x_max': 150,
        'gyro_y_max': 150,
        'gyro_z_max': 150,
        
        # Movement smoothness
        'jerk_max': 50,  # Rate of acceleration change
        
        # Asymmetry (left vs right)
        'asymmetry_max': 0.15,  # 15% difference is concerning
    }
    
    # Exercise-specific feedback
    EXERCISE_FEEDBACK = {
        'squat': {
            'correct': [
                "Great depth! Keep knees aligned over toes.",
                "Perfect form! Chest up, core engaged.",
                "Excellent! Controlled descent and rise."
            ],
            'incorrect_patterns': {
                'knee_valgus': "⚠️ Knees caving inward - push knees outward",
                'forward_lean': "⚠️ Leaning too far forward - keep chest up",
                'asymmetry': "⚠️ Weight shifted to one side - balance evenly",
                'fast_descent': "⚠️ Descending too quickly - slow and controlled",
                'shallow_depth': "⚠️ Not deep enough - aim for thighs parallel to ground",
                'heel_lift': "⚠️ Heels lifting - keep feet flat"
            }
        },
        'hip_abduction_left': {
            'correct': [
                "Perfect! Controlled leg lift.",
                "Great form! Keep hips stable.",
                "Excellent! Full range of motion."
            ],
            'incorrect_patterns': {
                'hip_rotation': "⚠️ Hip rotating - keep pelvis stable",
                'torso_lean': "⚠️ Leaning sideways - keep torso upright",
                'knee_bent': "⚠️ Knee bending - keep leg straight",
                'too_fast': "⚠️ Moving too quickly - slow and controlled",
                'insufficient_lift': "⚠️ Not lifting high enough - aim for 45°"
            }
        },
        'hip_adduction_right': {
            'correct': [
                "Perfect! Controlled movement.",
                "Great form! Stable pelvis.",
                "Excellent! Good range of motion."
            ],
            'incorrect_patterns': {
                'hip_rotation': "⚠️ Hip rotating - stabilize pelvis",
                'torso_lean': "⚠️ Leaning - keep torso straight",
                'too_fast': "⚠️ Too fast - slow it down"
            }
        },
        'knee_flexion_left': {
            'correct': [
                "Perfect! Smooth knee bend.",
                "Great! Full flexion achieved.",
                "Excellent! Controlled movement."
            ],
            'incorrect_patterns': {
                'hip_compensation': "⚠️ Hip bending too much - isolate knee",
                'foot_position': "⚠️ Foot position off - keep ankle stable",
                'jerky_motion': "⚠️ Jerky movement - smooth and controlled"
            }
        },
        'knee_flexion_right': {
            'correct': [
                "Perfect! Good knee isolation.",
                "Great! Full range achieved.",
                "Excellent! Smooth motion."
            ],
            'incorrect_patterns': {
                'hip_compensation': "⚠️ Too much hip movement - focus on knee",
                'foot_position': "⚠️ Foot unstable - maintain position",
                'jerky_motion': "⚠️ Too jerky - move smoothly"
            }
        }
    }
    
    def __init__(self, model_path: str = None):
        self.model = None
        self.feature_names = None
        self.model_type = None
        
        if model_path:
            self.load_model(model_path)
    
    def load_model(self, model_path: str):
        """Load trained form classifier"""
        model_data = joblib.load(model_path)
        self.model = model_data['model']
        self.feature_names = model_data['feature_names']
        self.model_type = model_data['model_type']
        print(f"✅ Form classifier loaded from: {model_path}")
    
    def analyze_form(self, features: np.ndarray, exercise_type: str) -> Dict:
        """
        Analyze exercise form and generate feedback
        
        Args:
            features: Feature vector (must match training features)
            exercise_type: 'squat', 'hip_abduction_left', etc.
        
        Returns:
            dict with prediction, probability, feedback, and issues
        """
        if self.model is None:
            return {
                'error': 'Model not loaded',
                'prediction': 0,
                'probability': 0.5,
                'feedback': 'Unable to analyze form'
            }
        
        # Ensure features is 2D
        if len(features.shape) == 1:
            features = features.reshape(1, -1)
        
        # Predict
        prediction = self.model.predict(features)[0]
        probabilities = self.model.predict_proba(features)[0]
        
        correct_prob = probabilities[1]
        is_correct = prediction == 1
        
        # Generate feedback
        feedback_dict = {
            'prediction': int(prediction),
            'correct_probability': float(correct_prob),
            'form_quality': f"{correct_prob*100:.1f}%",
            'is_correct': bool(is_correct),
            'feedback': [],
            'issues_detected': [],
            'corrections': []
        }
        
        # Get exercise-specific feedback
        exercise_feedback = self.EXERCISE_FEEDBACK.get(exercise_type, {})
        
        if is_correct:
            # Good form - positive feedback
            correct_messages = exercise_feedback.get('correct', ["Good form!"])
            feedback_dict['feedback'] = [np.random.choice(correct_messages)]
            feedback_dict['corrections'] = ["Keep it up! Maintain this form."]
        else:
            # Incorrect form - identify issues
            issues = self._detect_issues(features, exercise_type)
            feedback_dict['issues_detected'] = issues
            
            # Get specific corrections
            incorrect_patterns = exercise_feedback.get('incorrect_patterns', {})
            corrections = [incorrect_patterns.get(issue, f"⚠️ Form issue: {issue}") 
                          for issue in issues[:3]]  # Top 3 issues
            
            if not corrections:
                corrections = ["⚠️ Form needs improvement - check alignment and control"]
            
            feedback_dict['feedback'] = corrections
            feedback_dict['corrections'] = corrections
        
        return feedback_dict
    
    def _detect_issues(self, features: np.ndarray, exercise_type: str) -> List[str]:
        """
        Detect specific form issues from feature values
        
        Uses feature importance and thresholds to identify problems
        """
        issues = []
        
        if len(features.shape) == 1:
            features_flat = features
        else:
            features_flat = features[0]
        
        # Create feature dict
        feature_dict = dict(zip(self.feature_names, features_flat))
        
        # Check for common issues based on feature values
        
        # 1. Asymmetry detection (if left/right features exist)
        left_features = [f for f in self.feature_names if 'left' in f.lower() or 'lshin' in f.lower() or 'lthigh' in f.lower()]
        right_features = [f for f in self.feature_names if 'right' in f.lower() or 'rshin' in f.lower() or 'rthigh' in f.lower()]
        
        if left_features and right_features:
            left_vals = [feature_dict.get(f, 0) for f in left_features]
            right_vals = [feature_dict.get(f, 0) for f in right_features]
            
            left_mean = np.mean(np.abs(left_vals))
            right_mean = np.mean(np.abs(right_vals))
            
            if left_mean > 0 and right_mean > 0:
                asymmetry = abs(left_mean - right_mean) / max(left_mean, right_mean)
                if asymmetry > self.THRESHOLDS['asymmetry_max']:
                    issues.append('asymmetry')
        
        # 2. Excessive acceleration (jerky movements)
        accel_features = [f for f in self.feature_names if 'accel' in f.lower() and 'mean' in f.lower()]
        if accel_features:
            accel_vals = [abs(feature_dict.get(f, 0)) for f in accel_features]
            max_accel = max(accel_vals) if accel_vals else 0
            
            if max_accel > 15:  # High acceleration
                if 'squat' in exercise_type:
                    issues.append('fast_descent')
                else:
                    issues.append('too_fast')
        
        # 3. Rotation/twisting (gyroscope)
        gyro_features = [f for f in self.feature_names if 'gyro' in f.lower() and 'std' in f.lower()]
        if gyro_features:
            gyro_vals = [abs(feature_dict.get(f, 0)) for f in gyro_features]
            max_gyro = max(gyro_vals) if gyro_vals else 0
            
            if max_gyro > 100:
                if 'hip' in exercise_type:
                    issues.append('hip_rotation')
                elif 'squat' in exercise_type:
                    issues.append('knee_valgus')
        
        # 4. Range of motion issues (low variance)
        std_features = [f for f in self.feature_names if 'std' in f.lower()]
        if std_features:
            std_vals = [feature_dict.get(f, 0) for f in std_features]
            avg_std = np.mean(std_vals) if std_vals else 0
            
            if avg_std < 1.0:  # Low movement variation
                if 'squat' in exercise_type:
                    issues.append('shallow_depth')
                elif 'hip' in exercise_type:
                    issues.append('insufficient_lift')
        
        # 5. Exercise-specific checks
        if 'squat' in exercise_type:
            # Check for forward lean (high accel_x)
            accel_x_features = [f for f in self.feature_names if 'accel_x' in f.lower() and 'mean' in f.lower()]
            if accel_x_features:
                accel_x = feature_dict.get(accel_x_features[0], 0)
                if abs(accel_x) > 5:
                    issues.append('forward_lean')
        
        elif 'hip' in exercise_type:
            # Check for torso compensation
            torso_features = [f for f in self.feature_names if 'thigh' in f.lower() and 'gyro' in f.lower()]
            if torso_features:
                torso_rotation = max([abs(feature_dict.get(f, 0)) for f in torso_features], default=0)
                if torso_rotation > 80:
                    issues.append('torso_lean')
        
        elif 'knee' in exercise_type:
            # Check for hip compensation
            hip_features = [f for f in self.feature_names if 'thigh' in f.lower() and 'accel' in f.lower()]
            if hip_features:
                hip_movement = max([abs(feature_dict.get(f, 0)) for f in hip_features], default=0)
                if hip_movement > 8:
                    issues.append('hip_compensation')
        
        # If no specific issues found but form is incorrect
        if not issues:
            issues.append('general_form_issue')
        
        return issues
    
    def get_correction_priority(self, issues: List[str]) -> List[str]:
        """
        Order corrections by priority (most critical first)
        """
        priority_order = [
            'asymmetry',           # Safety concern
            'knee_valgus',         # Injury risk
            'forward_lean',        # Injury risk
            'hip_rotation',        # Compensation pattern
            'fast_descent',        # Control issue
            'too_fast',            # Control issue
            'shallow_depth',       # Effectiveness
            'insufficient_lift',   # Effectiveness
            'general_form_issue'   # Generic
        ]
        
        sorted_issues = []
        for priority_issue in priority_order:
            if priority_issue in issues:
                sorted_issues.append(priority_issue)
        
        # Add any remaining issues
        for issue in issues:
            if issue not in sorted_issues:
                sorted_issues.append(issue)
        
        return sorted_issues


# Example usage
if __name__ == '__main__':
    # Test the feedback generator
    print("🏥 Form Feedback Generator - Test Mode\n")
    
    # Load model
    model_path = './models/form_classifier/form_classifier_rf.pkl'
    
    if Path(model_path).exists():
        generator = FormFeedbackGenerator(model_path)
        
        print("✅ Model loaded successfully!")
        print(f"Features expected: {len(generator.feature_names)}")
        print(f"Model type: {generator.model_type}")
        
        # Create dummy features for testing
        dummy_features = np.random.randn(len(generator.feature_names))
        
        print("\n📊 Analyzing sample exercise...")
        result = generator.analyze_form(dummy_features, 'squat')
        
        print(f"\nForm Quality: {result['form_quality']}")
        print(f"Prediction: {'✅ Correct' if result['is_correct'] else '❌ Incorrect'}")
        print(f"\nFeedback:")
        for feedback in result['feedback']:
            print(f"  {feedback}")
        
        if result['issues_detected']:
            print(f"\nIssues Detected:")
            for issue in result['issues_detected']:
                print(f"  - {issue}")
    else:
        print(f"❌ Model not found at: {model_path}")
        print("   Train the model first: python train_form_classifier.py")
