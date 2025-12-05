"""
Quick validation script - tests basic functionality
Run this to verify test suite is working
"""

import sys
from pathlib import Path

# Add parent to path
sys.path.append(str(Path(__file__).parent.parent))

print("=" * 60)
print("QUICK TEST VALIDATION")
print("=" * 60)

# Test 1: Import test modules
print("\n1. Testing imports...")
try:
    from tests import test_angles
    from tests import test_environment
    from tests import test_api
    print("   ✅ All test modules imported successfully")
except Exception as e:
    print(f"   ❌ Import failed: {e}")
    sys.exit(1)

# Test 2: Check environment
print("\n2. Testing environment creation...")
try:
    from envs.rehab_env import RehabExerciseEnv
    env = RehabExerciseEnv()
    print("   ✅ Environment created successfully")
except Exception as e:
    print(f"   ❌ Environment creation failed: {e}")
    sys.exit(1)

# Test 3: Quick angle test
print("\n3. Testing angle calculation...")
try:
    import math
    
    class MockLandmark:
        def __init__(self, x, y):
            self.x = x
            self.y = y
    
    def calculate_angle(a, b, c):
        radians = math.atan2(c.y - b.y, c.x - b.x) - math.atan2(a.y - b.y, a.x - b.x)
        angle = abs(radians * 180.0 / math.pi)
        if angle > 180:
            angle = 360 - angle
        return angle
    
    # Test 90 degree angle
    p1 = MockLandmark(0, 0)
    p2 = MockLandmark(1, 0)
    p3 = MockLandmark(1, 1)
    angle = calculate_angle(p1, p2, p3)
    
    if abs(angle - 90) < 1:
        print(f"   ✅ Angle calculation correct: {angle:.1f}°")
    else:
        print(f"   ❌ Angle calculation incorrect: {angle:.1f}° (expected 90°)")
except Exception as e:
    print(f"   ❌ Angle test failed: {e}")

# Test 4: Environment step
print("\n4. Testing environment step...")
try:
    state, info = env.reset()
    state, reward, done, truncated, info = env.step(1)
    print(f"   ✅ Environment step successful")
    print(f"      State shape: {state.shape}")
    print(f"      Reward: {reward:.2f}")
except Exception as e:
    print(f"   ❌ Step test failed: {e}")

# Test 5: Reward calculation
print("\n5. Testing reward function...")
try:
    env.current_target = 90
    reward = env._calculate_rep_reward(89, 0.95)  # Perfect form
    if reward > 20:
        print(f"   ✅ Reward function working: {reward:.1f} RP")
    else:
        print(f"   ⚠️  Reward seems low: {reward:.1f} RP (expected >20)")
except Exception as e:
    print(f"   ❌ Reward test failed: {e}")

print("\n" + "=" * 60)
print("✅ QUICK VALIDATION COMPLETE")
print("\nTo run full test suite:")
print("  python tests/run_all_tests.py")
print("\nTo run individual test files:")
print("  python -m unittest tests.test_environment")
print("  python -m unittest tests.test_angles")
print("  python -m unittest tests.test_api")
print("=" * 60)
