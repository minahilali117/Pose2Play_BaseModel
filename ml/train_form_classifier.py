"""
Form Classification Model for Rehabilitation Exercises
Trains a classifier to detect correct vs incorrect exercise form

Focuses on: Hip, Knee, and Shoulder exercises
Dataset labels: 0 = incorrect form, 1 = correct form
"""

import os
import pandas as pd
import numpy as np
from pathlib import Path
import json
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.model_selection import cross_val_score
import joblib
import argparse

class FormClassifier:
    """Train and evaluate form classification model"""
    
    # Exercise codes for hip, knee, shoulder
    TARGET_EXERCISES = {
        'HAAL': 'hip_abduction_left',
        'HAAR': 'hip_adduction_right',
        'KFEL': 'knee_flexion_left',
        'KFER': 'knee_flexion_right',
        'SQT': 'squat',  # Knee exercise
        # Shoulder exercises would be in upper/ folder
    }
    
    def __init__(self, data_path: str, model_type: str = 'rf'):
        self.data_path = Path(data_path)
        self.model_type = model_type
        self.model = None
        self.feature_names = None
        
    def load_data(self):
        """Load processed training data"""
        print("\n📂 Loading dataset...")
        
        train_file = self.data_path / 'train.csv'
        val_file = self.data_path / 'val.csv'
        test_file = self.data_path / 'test.csv'
        
        if not all([train_file.exists(), val_file.exists(), test_file.exists()]):
            print("❌ Error: Processed data not found!")
            print("   Run: python data_processor.py --input ../Dataset --output ./data/processed")
            return None, None, None, None, None, None
        
        train_df = pd.read_csv(train_file)
        val_df = pd.read_csv(val_file)
        test_df = pd.read_csv(test_file)
        
        # Filter for hip/knee/shoulder exercises only
        exercise_col = 'exercise_type' if 'exercise_type' in train_df.columns else 'exercise'
        
        train_filtered = train_df[train_df[exercise_col].isin(self.TARGET_EXERCISES.values())]
        val_filtered = val_df[val_df[exercise_col].isin(self.TARGET_EXERCISES.values())]
        test_filtered = test_df[test_df[exercise_col].isin(self.TARGET_EXERCISES.values())]
        
        print(f"   Original dataset: {len(train_df)} train, {len(val_df)} val, {len(test_df)} test")
        print(f"   Filtered (hip/knee/shoulder): {len(train_filtered)} train, {len(val_filtered)} val, {len(test_filtered)} test")
        
        if len(train_filtered) == 0:
            print("⚠️  No hip/knee/shoulder exercises found. Using all exercises...")
            train_filtered = train_df
            val_filtered = val_df
            test_filtered = test_df
        
        # Separate features and labels
        # Label column is 'correct' (0 or 1)
        label_col = 'correct' if 'correct' in train_filtered.columns else 'label'
        
        # Drop non-feature columns
        drop_cols = ['exercise_code', 'exercise', label_col, 'subject', 'trial', 'repetition', 'filename', 'sensor_position']
        drop_cols = [col for col in drop_cols if col in train_filtered.columns]
        
        X_train = train_filtered.drop(columns=drop_cols)
        y_train = train_filtered[label_col]
        
        X_val = val_filtered.drop(columns=drop_cols)
        y_val = val_filtered[label_col]
        
        X_test = test_filtered.drop(columns=drop_cols)
        y_test = test_filtered[label_col]
        
        self.feature_names = X_train.columns.tolist()
        
        print(f"\n📊 Dataset Summary:")
        print(f"   Features: {len(self.feature_names)}")
        print(f"   Training samples: {len(X_train)} (Correct: {sum(y_train)}, Incorrect: {len(y_train) - sum(y_train)})")
        print(f"   Validation samples: {len(X_val)} (Correct: {sum(y_val)}, Incorrect: {len(y_val) - sum(y_val)})")
        print(f"   Test samples: {len(X_test)} (Correct: {sum(y_test)}, Incorrect: {len(y_test) - sum(y_test)})")
        
        return X_train, X_val, X_test, y_train, y_val, y_test
    
    def build_model(self):
        """Build classification model"""
        print(f"\n🔨 Building {self.model_type.upper()} model...")
        
        if self.model_type == 'rf':
            # Random Forest - good for interpretability
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            )
            print("   Model: Random Forest")
            print("   Trees: 100, Max depth: 10")
            
        elif self.model_type == 'mlp':
            # Neural Network - higher capacity
            self.model = MLPClassifier(
                hidden_layer_sizes=(128, 64, 32),
                activation='relu',
                solver='adam',
                max_iter=500,
                random_state=42,
                early_stopping=True,
                validation_fraction=0.1
            )
            print("   Model: Multi-Layer Perceptron")
            print("   Architecture: 128 → 64 → 32 → 2")
        
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")
    
    def train(self, X_train, y_train, X_val, y_val):
        """Train the model"""
        print("\n🚀 Training model...")
        
        self.model.fit(X_train, y_train)
        
        # Training accuracy
        train_acc = self.model.score(X_train, y_train)
        print(f"   Training accuracy: {train_acc:.3f}")
        
        # Validation accuracy
        val_acc = self.model.score(X_val, y_val)
        print(f"   Validation accuracy: {val_acc:.3f}")
        
        # Cross-validation
        print("\n📊 Cross-validation (5-fold)...")
        cv_scores = cross_val_score(self.model, X_train, y_train, cv=5, n_jobs=-1)
        print(f"   CV accuracy: {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")
        
        return train_acc, val_acc
    
    def evaluate(self, X_test, y_test):
        """Evaluate on test set"""
        print("\n🧪 Evaluating on test set...")
        
        y_pred = self.model.predict(X_test)
        y_proba = self.model.predict_proba(X_test)
        
        # Accuracy
        acc = accuracy_score(y_test, y_pred)
        print(f"\n✅ Test Accuracy: {acc:.3f}")
        
        # Classification report
        print("\n📋 Classification Report:")
        print(classification_report(y_test, y_pred, 
                                     target_names=['Incorrect Form', 'Correct Form']))
        
        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred)
        print("\n🔢 Confusion Matrix:")
        print("                 Predicted")
        print("               Incorrect  Correct")
        print(f"Actual Incorrect    {cm[0][0]:4d}     {cm[0][1]:4d}")
        print(f"       Correct      {cm[1][0]:4d}     {cm[1][1]:4d}")
        
        # Feature importance (if Random Forest)
        if self.model_type == 'rf':
            print("\n🎯 Top 10 Most Important Features:")
            importances = self.model.feature_importances_
            indices = np.argsort(importances)[::-1][:10]
            
            for i, idx in enumerate(indices, 1):
                print(f"   {i}. {self.feature_names[idx]}: {importances[idx]:.4f}")
        
        return acc, y_pred, y_proba
    
    def save_model(self, output_path: str):
        """Save trained model"""
        output_dir = Path(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        model_file = output_dir / f'form_classifier_{self.model_type}.pkl'
        
        # Save model + metadata
        model_data = {
            'model': self.model,
            'feature_names': self.feature_names,
            'model_type': self.model_type,
            'target_exercises': self.TARGET_EXERCISES
        }
        
        joblib.dump(model_data, model_file)
        print(f"\n💾 Model saved to: {model_file}")
        
        # Save feature names as JSON
        feature_file = output_dir / 'feature_names.json'
        with open(feature_file, 'w') as f:
            json.dump(self.feature_names, f, indent=2)
        
        return str(model_file)
    
    def load_model(self, model_path: str):
        """Load trained model"""
        model_data = joblib.load(model_path)
        self.model = model_data['model']
        self.feature_names = model_data['feature_names']
        self.model_type = model_data['model_type']
        print(f"✅ Model loaded from: {model_path}")
        return self.model
    
    def predict_form(self, features: np.ndarray):
        """
        Predict form correctness
        
        Args:
            features: Array of shape (n_features,) or (n_samples, n_features)
        
        Returns:
            dict with 'correct_probability', 'prediction', 'confidence'
        """
        if self.model is None:
            raise ValueError("Model not trained or loaded!")
        
        # Ensure 2D array
        if len(features.shape) == 1:
            features = features.reshape(1, -1)
        
        # Predict
        prediction = self.model.predict(features)[0]
        probabilities = self.model.predict_proba(features)[0]
        
        return {
            'prediction': int(prediction),  # 0 = incorrect, 1 = correct
            'correct_probability': float(probabilities[1]),
            'incorrect_probability': float(probabilities[0]),
            'confidence': float(max(probabilities)),
            'form_quality': f"{probabilities[1]*100:.1f}%"
        }


def main():
    parser = argparse.ArgumentParser(description='Train form classification model')
    parser.add_argument('--data', type=str, default='./data/processed',
                        help='Path to processed data directory')
    parser.add_argument('--model', type=str, default='rf', choices=['rf', 'mlp'],
                        help='Model type: rf (Random Forest) or mlp (Neural Network)')
    parser.add_argument('--output', type=str, default='./models/form_classifier',
                        help='Output directory for trained model')
    args = parser.parse_args()
    
    print("=" * 60)
    print("🏥 FORM CLASSIFICATION MODEL TRAINING")
    print("=" * 60)
    print(f"Target exercises: Hip, Knee, Shoulder")
    print(f"Model type: {args.model.upper()}")
    
    # Initialize classifier
    classifier = FormClassifier(args.data, model_type=args.model)
    
    # Load data
    X_train, X_val, X_test, y_train, y_val, y_test = classifier.load_data()
    
    if X_train is None:
        return
    
    # Build model
    classifier.build_model()
    
    # Train
    train_acc, val_acc = classifier.train(X_train, y_train, X_val, y_val)
    
    # Evaluate
    test_acc, y_pred, y_proba = classifier.evaluate(X_test, y_test)
    
    # Save model
    model_path = classifier.save_model(args.output)
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ TRAINING COMPLETE!")
    print("=" * 60)
    print(f"Training accuracy:   {train_acc:.3f}")
    print(f"Validation accuracy: {val_acc:.3f}")
    print(f"Test accuracy:       {test_acc:.3f}")
    print(f"\nModel saved to: {model_path}")
    print("\nNext steps:")
    print("1. Test the model: python test_form_classifier.py")
    print("2. Integrate into API: python api_server.py")
    print("3. Use in demo: Open demo/index.html")
    print("=" * 60)


if __name__ == '__main__':
    main()
