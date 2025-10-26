"""
Test Form Tips Feature
Tests that the form quality tips are being generated correctly
"""

import requests
import json

API_URL = 'http://localhost:5000'

def test_form_tips():
    """Test that form analysis returns helpful tips"""
    
    print("🧪 TESTING FORM TIPS FEATURE\n")
    
    # Test 1: Good squat form
    print("1️⃣ Testing Good Squat Form...")
    response = requests.post(f'{API_URL}/predict_form_simple', json={
        'angles': {'knee_left': 85, 'knee_right': 87},
        'movement_speed': 2.5,
        'exercise_type': 'squat'
    })
    result = response.json()
    print(f"   Form Quality: {result['form_quality']}")
    print(f"   Status: {result['is_correct']}")
    print(f"   Feedback: {result.get('feedback', [])}")
    print(f"   Issues: {result.get('issues', [])}")
    print()
    
    # Test 2: Shallow squat (should get tips to squat deeper)
    print("2️⃣ Testing Shallow Squat (needs tips)...")
    response = requests.post(f'{API_URL}/predict_form_simple', json={
        'angles': {'knee_left': 110, 'knee_right': 112},
        'movement_speed': 2.5,
        'exercise_type': 'squat'
    })
    result = response.json()
    print(f"   Form Quality: {result['form_quality']}")
    print(f"   Status: {result['is_correct']}")
    print(f"   Corrections: {result.get('corrections', [])}")
    print(f"   Issues: {result.get('issues', [])}")
    print()
    
    # Test 3: Asymmetric squat (should get balance tips)
    print("3️⃣ Testing Asymmetric Squat (needs balance tips)...")
    response = requests.post(f'{API_URL}/predict_form_simple', json={
        'angles': {'knee_left': 80, 'knee_right': 100},
        'movement_speed': 2.5,
        'exercise_type': 'squat'
    })
    result = response.json()
    print(f"   Form Quality: {result['form_quality']}")
    print(f"   Corrections: {result.get('corrections', [])}")
    print(f"   Issues: {result.get('issues', [])}")
    print()
    
    # Test 4: Fast movement (should get speed tips)
    print("4️⃣ Testing Fast Movement (needs tempo tips)...")
    response = requests.post(f'{API_URL}/predict_form_simple', json={
        'angles': {'knee_left': 88, 'knee_right': 90},
        'movement_speed': 1.0,  # Too fast
        'exercise_type': 'squat'
    })
    result = response.json()
    print(f"   Form Quality: {result['form_quality']}")
    print(f"   Corrections: {result.get('corrections', [])}")
    print(f"   Issues: {result.get('issues', [])}")
    print()
    
    # Test 5: Hip exercise
    print("5️⃣ Testing Hip Exercise...")
    response = requests.post(f'{API_URL}/predict_form_simple', json={
        'angles': {'hip_left': 130},
        'movement_speed': 2.5,
        'exercise_type': 'hip_abduction_left'
    })
    result = response.json()
    print(f"   Form Quality: {result['form_quality']}")
    print(f"   Corrections: {result.get('corrections', [])}")
    print(f"   Issues: {result.get('issues', [])}")
    print()
    
    # Test 6: Shoulder exercise
    print("6️⃣ Testing Shoulder Exercise...")
    response = requests.post(f'{API_URL}/predict_form_simple', json={
        'angles': {'shoulder_left': 70},  # Too low
        'movement_speed': 2.5,
        'exercise_type': 'shoulder'
    })
    result = response.json()
    print(f"   Form Quality: {result['form_quality']}")
    print(f"   Corrections: {result.get('corrections', [])}")
    print(f"   Issues: {result.get('issues', [])}")
    print()
    
    print("✅ Form tips test complete!")
    print("\n💡 Tips should now appear in the demo UI under 'Tips to Improve Form' panel")
    print("   The tips are generated client-side based on form quality and detected issues")

if __name__ == '__main__':
    try:
        # First check if API is running
        response = requests.get(f'{API_URL}/health')
        if response.status_code != 200:
            print("❌ API server not running!")
            print("   Start it with: .\\START_PHASE7.ps1")
            exit(1)
        
        test_form_tips()
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API server!")
        print("   Make sure to start it first: .\\START_PHASE7.ps1")
        exit(1)
