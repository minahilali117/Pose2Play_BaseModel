"""
Quick test script to verify ML setup and environment
Run this first to check everything is working!
"""

import sys
from pathlib import Path

def test_imports():
    """Test if all required libraries are installed"""
    print("🧪 Testing imports...")
    
    try:
        import numpy as np
        print("  ✅ NumPy:", np.__version__)
    except ImportError:
        print("  ❌ NumPy not found - run: pip install numpy")
        return False
    
    try:
        import pandas as pd
        print("  ✅ Pandas:", pd.__version__)
    except ImportError:
        print("  ❌ Pandas not found - run: pip install pandas")
        return False
    
    try:
        import gym
        print("  ✅ Gym:", gym.__version__)
    except ImportError:
        print("  ❌ Gym not found - run: pip install gym")
        return False
    
    try:
        import stable_baselines3 as sb3
        print("  ✅ Stable-Baselines3:", sb3.__version__)
    except ImportError:
        print("  ❌ Stable-Baselines3 not found - run: pip install stable-baselines3")
        return False
    
    try:
        import matplotlib
        print("  ✅ Matplotlib:", matplotlib.__version__)
    except ImportError:
        print("  ⚠️  Matplotlib not found (optional) - run: pip install matplotlib")
    
    return True

def test_environment():
    """Test custom rehabilitation environment"""
    print("\n🏋️ Testing Rehabilitation Environment...")
    
    try:
        from envs.rehab_env import RehabExerciseEnv
        
        # Create environment
        env = RehabExerciseEnv()
        print("  ✅ Environment created")
        
        # Test reset
        state = env.reset()
        print(f"  ✅ Reset successful - State shape: {state.shape}")
        
        # Test step
        action = env.action_space.sample()
        state, reward, done, info = env.step(action)
        print(f"  ✅ Step successful - Reward: {reward:.2f}")
        
        # Test multiple steps
        for _ in range(5):
            action = env.action_space.sample()
            state, reward, done, info = env.step(action)
            if done:
                break
        
        print(f"  ✅ Environment fully functional!")
        return True
        
    except Exception as e:
        print(f"  ❌ Environment test failed: {e}")
        return False

def test_dataset():
    """Check if dataset is accessible"""
    print("\n📊 Testing Dataset Access...")
    
    dataset_path = Path("../Dataset")
    
    if not dataset_path.exists():
        print(f"  ❌ Dataset not found at: {dataset_path.absolute()}")
        print("     Please ensure Dataset folder is in correct location")
        return False
    
    # Check for inertial data
    inertial_path = dataset_path / "inertial" / "lower" / "A"
    if inertial_path.exists():
        csv_files = list(inertial_path.glob("*/*.csv"))
        print(f"  ✅ Dataset found")
        print(f"     Location: {dataset_path.absolute()}")
        print(f"     Sample files: {len(csv_files)}")
        return True
    else:
        print(f"  ⚠️  Dataset structure unexpected")
        return False

def test_data_processor():
    """Test data processor"""
    print("\n🔄 Testing Data Processor...")
    
    try:
        from data_processor import RehabDataProcessor
        print("  ✅ Data processor imported successfully")
        
        # Note: We don't run full processing here (too slow for quick test)
        print("  ℹ️  Run full processing with: python data_processor.py --input ../Dataset --output ./data/processed")
        return True
        
    except Exception as e:
        print(f"  ❌ Data processor test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("="*60)
    print("🚀 Pose2Play ML System Test Suite")
    print("="*60)
    
    results = []
    
    # Test 1: Imports
    results.append(("Imports", test_imports()))
    
    # Test 2: Environment
    results.append(("Environment", test_environment()))
    
    # Test 3: Dataset
    results.append(("Dataset", test_dataset()))
    
    # Test 4: Data Processor
    results.append(("Data Processor", test_data_processor()))
    
    # Summary
    print("\n" + "="*60)
    print("📋 Test Summary")
    print("="*60)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}: {name}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n🎉 All tests passed! You're ready to train!")
        print("\n📝 Next steps:")
        print("  1. Process dataset: python data_processor.py --input ../Dataset --output ./data/processed")
        print("  2. Train RL agent: python train_rl.py --algorithm DQN --timesteps 100000")
        print("  3. Evaluate model: python train_rl.py --mode eval --model ./models/dqn/DQN_rehab_final.zip")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above before proceeding.")
    
    print("="*60)

if __name__ == '__main__':
    main()
