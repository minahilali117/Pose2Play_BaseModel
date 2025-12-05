"""
Master test runner - executes all unit tests and generates summary
Run with: python tests/run_all_tests.py
"""

import unittest
import sys
import os
from pathlib import Path
import time

# Add parent directory and tests directory to path
parent_dir = Path(__file__).parent.parent
tests_dir = Path(__file__).parent
sys.path.insert(0, str(parent_dir))
sys.path.insert(0, str(tests_dir))

# Import test modules directly (avoid conflict with builtin 'tests' package)
import test_environment
import test_angles
import test_api


def run_all_tests():
    """Run all test suites and generate summary"""
    
    print("="*70)
    print("POSE2PLAY - COMPREHENSIVE UNIT TEST SUITE")
    print("="*70)
    print()
    
    # Create test loader
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test modules
    test_modules = [
        ('Environment Tests', test_environment),
        ('Angle Calculation Tests', test_angles),
        ('API Tests', test_api)
    ]
    
    # Load tests
    print("Loading test suites...")
    for name, module in test_modules:
        tests = loader.loadTestsFromModule(module)
        suite.addTests(tests)
        print(f"  ✓ {name}: {tests.countTestCases()} tests")
    
    print(f"\nTotal tests to run: {suite.countTestCases()}")
    print("="*70)
    print()
    
    # Run tests
    start_time = time.time()
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    duration = time.time() - start_time
    
    # Generate summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    tests_run = result.testsRun
    successes = tests_run - len(result.failures) - len(result.errors)
    failures = len(result.failures)
    errors = len(result.errors)
    skipped = len(result.skipped)
    
    print(f"Tests Run:     {tests_run}")
    print(f"Successes:     {successes}")
    print(f"Failures:      {failures}")
    print(f"Errors:        {errors}")
    print(f"Skipped:       {skipped}")
    print(f"Duration:      {duration:.2f}s")
    print()
    
    # Category breakdown
    print("CATEGORY BREAKDOWN:")
    print("-" * 70)
    
    categories = {
        'Angle Calculation': 0,
        'State Machine': 0,
        'Reward Calculation': 0,
        'Adaptive Adjustment': 0,
        'RL State Vector': 0,
        'RL Reward Function': 0,
        'Form Analysis API': 0
    }
    
    # Count tests per category (approximate based on test class names)
    for test_case in suite:
        test_name = str(test_case)
        
        if 'TestAngle' in test_name:
            categories['Angle Calculation'] += 1
        elif 'TestEnvironmentStep' in test_name or 'TestSessionCompletion' in test_name:
            categories['State Machine'] += 1
        elif 'TestRewardFunction' in test_name:
            categories['RL Reward Function'] += 1
        elif 'TestDifficultyAdjustment' in test_name:
            categories['Adaptive Adjustment'] += 1
        elif 'TestStateVector' in test_name:
            categories['RL State Vector'] += 1
        elif 'TestFormAnalysisAPI' in test_name:
            categories['Form Analysis API'] += 1
    
    # Print category summary
    total_category_tests = 0
    for category, count in categories.items():
        if count > 0:
            status = "✅ Pass" if result.wasSuccessful() else "⚠️  Check"
            coverage = "100%" if result.wasSuccessful() else "Partial"
            print(f"{category:25} {count:2} tests    {coverage:8}    {status}")
            total_category_tests += count
    
    print("-" * 70)
    print(f"{'TOTAL':25} {total_category_tests:2} tests")
    print()
    
    # Detailed failures
    if failures > 0:
        print("FAILURES:")
        print("-" * 70)
        for test, traceback in result.failures:
            print(f"❌ {test}")
            print(f"   {traceback.split('AssertionError:')[-1].strip()[:100]}")
        print()
    
    if errors > 0:
        print("ERRORS:")
        print("-" * 70)
        for test, traceback in result.errors:
            print(f"❌ {test}")
            error_msg = traceback.strip().split('\n')[-1]
            print(f"   {error_msg[:100]}")
        print()
    
    if skipped > 0:
        print("SKIPPED:")
        print("-" * 70)
        for test, reason in result.skipped:
            print(f"⊘ {test}")
            print(f"   {reason}")
        print()
    
    # Final verdict
    print("="*70)
    if result.wasSuccessful():
        print("✅ ALL TESTS PASSED!")
        print()
        print("Your system is working correctly. You can proceed with:")
        print("  1. Training RL agents with improved parameters")
        print("  2. VR integration testing")
        print("  3. Deployment preparation")
    else:
        print("❌ SOME TESTS FAILED")
        print()
        print("Please review the failures above and fix the issues.")
        print("Common issues:")
        print("  - API server not running (start with: python api_server.py)")
        print("  - Missing dependencies (run: pip install -r requirements.txt)")
        print("  - Environment configuration issues")
    
    print("="*70)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
