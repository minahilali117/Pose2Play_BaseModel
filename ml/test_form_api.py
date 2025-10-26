"""
Test Form Classification System
Quick test to verify API and model are working
"""

import requests
import json

API_URL = "http://localhost:5000"

def test_health():
    """Test if API is running"""
    print("\n1️⃣  Testing API Health...")
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        data = response.json()
        
        print(f"   Status: {data['status']}")
        print(f"   RL Model: {'✅ Loaded' if data.get('rl_model_loaded') else '❌ Not loaded'}")
        print(f"   Form Classifier: {'✅ Loaded' if data.get('form_classifier_loaded') else '❌ Not loaded'}")
        
        return data['status'] == 'ok'
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_form_simple_good():
    """Test form analysis with good form"""
    print("\n2️⃣  Testing Good Form (Squat 85°, balanced)...")
    try:
        response = requests.post(
            f"{API_URL}/predict_form_simple",
            json={
                "angles": {
                    "knee_left": 85,
                    "knee_right": 87
                },
                "movement_speed": 2.5,
                "exercise_type": "squat"
            },
            timeout=5
        )
        
        data = response.json()
        print(f"   Form Quality: {data['form_quality']}")
        print(f"   Status: {'✅ Correct' if data['is_correct'] else '⚠️ Incorrect'}")
        print(f"   Feedback: {data['feedback']}")
        
        return data['is_correct']
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_form_simple_shallow():
    """Test form analysis with shallow squat"""
    print("\n3️⃣  Testing Shallow Squat (110°, too shallow)...")
    try:
        response = requests.post(
            f"{API_URL}/predict_form_simple",
            json={
                "angles": {
                    "knee_left": 110,
                    "knee_right": 108
                },
                "movement_speed": 2.8,
                "exercise_type": "squat"
            },
            timeout=5
        )
        
        data = response.json()
        print(f"   Form Quality: {data['form_quality']}")
        print(f"   Status: {'✅ Correct' if data['is_correct'] else '⚠️ Incorrect'}")
        print(f"   Corrections: {data['corrections']}")
        
        return not data['is_correct']  # Should be incorrect
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_form_simple_asymmetric():
    """Test form analysis with asymmetric squat"""
    print("\n4️⃣  Testing Asymmetric Squat (left 80°, right 100°)...")
    try:
        response = requests.post(
            f"{API_URL}/predict_form_simple",
            json={
                "angles": {
                    "knee_left": 80,
                    "knee_right": 100
                },
                "movement_speed": 2.5,
                "exercise_type": "squat"
            },
            timeout=5
        )
        
        data = response.json()
        print(f"   Form Quality: {data['form_quality']}")
        print(f"   Status: {'✅ Correct' if data['is_correct'] else '⚠️ Incorrect'}")
        print(f"   Corrections: {data['corrections']}")
        print(f"   Issues: {data['issues_detected']}")
        
        return 'asymmetry' in data['issues_detected']
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_form_simple_fast():
    """Test form analysis with fast movement"""
    print("\n5️⃣  Testing Fast Movement (1 second per rep)...")
    try:
        response = requests.post(
            f"{API_URL}/predict_form_simple",
            json={
                "angles": {
                    "knee_left": 88,
                    "knee_right": 90
                },
                "movement_speed": 1.0,  # Too fast!
                "exercise_type": "squat"
            },
            timeout=5
        )
        
        data = response.json()
        print(f"   Form Quality: {data['form_quality']}")
        print(f"   Status: {'✅ Correct' if data['is_correct'] else '⚠️ Incorrect'}")
        print(f"   Corrections: {data['corrections']}")
        
        return 'too_fast' in data['issues_detected']
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    print("=" * 60)
    print("🧪 FORM CLASSIFICATION SYSTEM - TEST SUITE")
    print("=" * 60)
    
    results = []
    
    # Test 1: API Health
    results.append(("API Health", test_health()))
    
    if not results[0][1]:
        print("\n❌ API not running! Start it with: .\\START_PHASE7.ps1")
        return
    
    # Test 2-5: Form analysis
    results.append(("Good Form Detection", test_form_simple_good()))
    results.append(("Shallow Squat Detection", test_form_simple_shallow()))
    results.append(("Asymmetry Detection", test_form_simple_asymmetric()))
    results.append(("Fast Movement Detection", test_form_simple_fast()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}  {test_name}")
    
    print("=" * 60)
    print(f"Score: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("\n🎉 All tests passed! Form classification is working perfectly!")
    else:
        print("\n⚠️  Some tests failed. Check API server logs.")
    
    print("=" * 60)

if __name__ == '__main__':
    main()
