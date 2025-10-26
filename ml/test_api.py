"""
Quick test script for the Flask API server.
Run this AFTER starting api_server.py to verify it's working.
"""

import requests
import numpy as np

def test_health():
    """Test the /health endpoint"""
    try:
        response = requests.get('http://localhost:5000/health')
        print("✅ Health Check:", response.json())
        return response.json().get('model_loaded', False)
    except Exception as e:
        print("❌ Health Check Failed:", str(e))
        return False

def test_predict():
    """Test the /predict endpoint with a sample state"""
    try:
        # Create a sample 20-dimensional state
        sample_state = [
            100, 95, 90, 88, 85, 90, 92, 95, 98, 100,  # Last 10 angles
            0.85,  # Consistency
            0.15,  # Fatigue
            0.3,   # Session time normalized
            90,    # Current target
            105,   # Baseline
            0.5,   # Reps completed normalized
            0.8,   # Success rate
            0, 0, 0  # Padding
        ]
        
        response = requests.post(
            'http://localhost:5000/predict',
            json={'state': sample_state}
        )
        
        result = response.json()
        print("✅ Predict Response:", result)
        
        action_names = ['Decrease', 'Maintain', 'Increase', 'Rest', 'Encourage']
        print(f"   Action: {result['action']} - {action_names[result['action']]}")
        
        return True
    except Exception as e:
        print("❌ Predict Test Failed:", str(e))
        return False

if __name__ == '__main__':
    print("=" * 50)
    print("🧪 Testing RL API Server")
    print("=" * 50)
    print("\nMake sure api_server.py is running first!")
    print("Run: python api_server.py\n")
    
    # Test health endpoint
    print("1. Testing /health endpoint...")
    model_loaded = test_health()
    
    if not model_loaded:
        print("\n⚠️ Model not loaded! Check that DQN_rehab_final.zip exists.")
        print("   Expected location: ./models/dqn/DQN_rehab_final.zip")
    
    # Test predict endpoint
    print("\n2. Testing /predict endpoint...")
    success = test_predict()
    
    if success:
        print("\n" + "=" * 50)
        print("✅ All tests passed! API is working correctly.")
        print("=" * 50)
        print("\nYou can now:")
        print("1. Open demo/index.html in your browser")
        print("2. Do 5+ squats to trigger RL adjustments")
        print("3. Watch the console for RL decisions")
    else:
        print("\n❌ Tests failed. Check api_server.py logs for errors.")
