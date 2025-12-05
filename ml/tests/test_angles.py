"""
Unit tests for angle calculation (JavaScript functions simulated in Python)
Tests: Angle Calculation
"""

import unittest
import numpy as np
import math


class MockLandmark:
    """Mock landmark object for testing"""
    def __init__(self, x, y, z=0):
        self.x = x
        self.y = y
        self.z = z


def calculate_angle(a, b, c):
    """
    Calculate angle between three points (JavaScript function ported to Python)
    b is the vertex (joint)
    Returns angle in degrees
    """
    # Calculate vectors
    radians = math.atan2(c.y - b.y, c.x - b.x) - math.atan2(a.y - b.y, a.x - b.x)
    
    # Convert to degrees
    angle = abs(radians * 180.0 / math.pi)
    
    # Normalize to 0-180
    if angle > 180:
        angle = 360 - angle
    
    return angle


class TestAngleCalculation(unittest.TestCase):
    """Test geometric angle calculations (Angle Calculation)"""
    
    def test_01_right_angle_90_degrees(self):
        """Test calculation of 90° angle"""
        p1 = MockLandmark(0, 0)      # Point A
        p2 = MockLandmark(1, 0)      # Point B (vertex)
        p3 = MockLandmark(1, 1)      # Point C
        
        angle = calculate_angle(p1, p2, p3)
        
        self.assertAlmostEqual(angle, 90, delta=1,
                              msg=f"Expected 90°, got {angle:.2f}°")
    
    def test_02_straight_line_180_degrees(self):
        """Test calculation of 180° angle (straight line)"""
        p1 = MockLandmark(0, 0)
        p2 = MockLandmark(1, 0)
        p3 = MockLandmark(2, 0)
        
        angle = calculate_angle(p1, p2, p3)
        
        self.assertAlmostEqual(angle, 180, delta=1,
                              msg=f"Expected 180°, got {angle:.2f}°")
    
    def test_03_acute_angle_45_degrees(self):
        """Test calculation of 45° angle"""
        p1 = MockLandmark(0, 0)
        p2 = MockLandmark(1, 0)
        p3 = MockLandmark(1.707, 0.707)  # 45° from horizontal
        
        angle = calculate_angle(p1, p2, p3)
        
        # Function returns interior angle (135° for this configuration)
        self.assertAlmostEqual(angle, 135, delta=2,
                              msg=f"Expected 135° interior angle, got {angle:.2f}°")
    
    def test_04_obtuse_angle_135_degrees(self):
        """Test calculation of 135° angle"""
        p1 = MockLandmark(0, 0)
        p2 = MockLandmark(1, 0)
        p3 = MockLandmark(0.293, 0.707)  # 135° from horizontal
        
        angle = calculate_angle(p1, p2, p3)
        
        # Function returns interior angle (45° for this configuration)
        self.assertAlmostEqual(angle, 45, delta=2,
                              msg=f"Expected 45° interior angle, got {angle:.2f}°")
    
    def test_05_squat_knee_angle_standing(self):
        """Test knee angle when standing (should be ~180°)"""
        hip = MockLandmark(0.5, 0.3)
        knee = MockLandmark(0.5, 0.6)
        ankle = MockLandmark(0.5, 0.9)
        
        angle = calculate_angle(hip, knee, ankle)
        
        # Standing should be close to 180°
        self.assertGreater(angle, 170, 
                          f"Standing knee angle should be >170°, got {angle:.2f}°")
    
    def test_06_squat_knee_angle_squatting(self):
        """Test knee angle when squatting (should be ~90°)"""
        hip = MockLandmark(0.5, 0.5)
        knee = MockLandmark(0.5, 0.7)
        ankle = MockLandmark(0.6, 0.7)
        
        angle = calculate_angle(hip, knee, ankle)
        
        # Squatting should be closer to 90°
        self.assertLess(angle, 120,
                       f"Squatting knee angle should be <120°, got {angle:.2f}°")
    
    def test_07_hip_flexion_angle_standing(self):
        """Test hip angle when standing (should be ~180°)"""
        shoulder = MockLandmark(0.5, 0.2)
        hip = MockLandmark(0.5, 0.5)
        knee = MockLandmark(0.5, 0.8)
        
        angle = calculate_angle(shoulder, hip, knee)
        
        self.assertGreater(angle, 170,
                          f"Standing hip angle should be >170°, got {angle:.2f}°")
    
    def test_08_hip_flexion_angle_raised(self):
        """Test hip angle with leg raised (should be ~90°)"""
        shoulder = MockLandmark(0.5, 0.2)
        hip = MockLandmark(0.5, 0.5)
        knee = MockLandmark(0.7, 0.5)  # Leg raised horizontally
        
        angle = calculate_angle(shoulder, hip, knee)
        
        self.assertLess(angle, 100,
                       f"Raised leg hip angle should be <100°, got {angle:.2f}°")
    
    def test_09_shoulder_angle_arm_down(self):
        """Test shoulder angle with arm down (should be small)"""
        hip = MockLandmark(0.5, 0.5)
        shoulder = MockLandmark(0.5, 0.2)
        elbow = MockLandmark(0.5, 0.3)
        
        angle = calculate_angle(hip, shoulder, elbow)
        
        self.assertLess(angle, 30,
                       f"Arm down shoulder angle should be <30°, got {angle:.2f}°")
    
    def test_10_shoulder_angle_arm_raised(self):
        """Test shoulder angle with arm raised (should be ~90°)"""
        hip = MockLandmark(0.5, 0.5)
        shoulder = MockLandmark(0.5, 0.2)
        elbow = MockLandmark(0.7, 0.2)  # Arm horizontal
        
        angle = calculate_angle(hip, shoulder, elbow)
        
        self.assertGreater(angle, 80,
                          f"Arm raised shoulder angle should be >80°, got {angle:.2f}°")
        self.assertLess(angle, 100,
                       f"Arm raised shoulder angle should be <100°, got {angle:.2f}°")
    
    def test_11_angle_always_positive(self):
        """Test that calculated angles are always positive"""
        # Test various random configurations
        for _ in range(100):
            p1 = MockLandmark(np.random.random(), np.random.random())
            p2 = MockLandmark(np.random.random(), np.random.random())
            p3 = MockLandmark(np.random.random(), np.random.random())
            
            angle = calculate_angle(p1, p2, p3)
            
            self.assertGreaterEqual(angle, 0, "Angle should be positive")
            self.assertLessEqual(angle, 180, "Angle should be ≤180°")
    
    def test_12_angle_symmetry(self):
        """Test that angle calculation is symmetric"""
        p1 = MockLandmark(0, 0)
        p2 = MockLandmark(1, 0)
        p3 = MockLandmark(1, 1)
        
        # Calculate angle both ways
        angle1 = calculate_angle(p1, p2, p3)
        angle2 = calculate_angle(p3, p2, p1)
        
        self.assertAlmostEqual(angle1, angle2, delta=0.1,
                              msg="Angle should be same regardless of order")


class TestAngleEdgeCases(unittest.TestCase):
    """Test edge cases for angle calculation"""
    
    def test_01_coincident_points(self):
        """Test angle with coincident points"""
        p1 = MockLandmark(0, 0)
        p2 = MockLandmark(0, 0)  # Same as p1
        p3 = MockLandmark(1, 1)
        
        # Should not crash
        angle = calculate_angle(p1, p2, p3)
        self.assertIsInstance(angle, (int, float))
    
    def test_02_very_small_angles(self):
        """Test calculation of very small angles"""
        p1 = MockLandmark(0, 0)
        p2 = MockLandmark(1, 0)
        p3 = MockLandmark(2, 0.01)  # Almost straight
        
        angle = calculate_angle(p1, p2, p3)
        
        # Nearly collinear points return ~180° (nearly straight line)
        self.assertGreater(angle, 175,
                       f"Nearly collinear should be >175°, got {angle:.2f}°")
    
    def test_03_normalized_coordinates(self):
        """Test with normalized coordinates (0-1 range, like MediaPipe)"""
        # MediaPipe returns normalized coordinates
        hip = MockLandmark(0.45, 0.62)
        knee = MockLandmark(0.46, 0.75)
        ankle = MockLandmark(0.47, 0.92)
        
        angle = calculate_angle(hip, knee, ankle)
        
        # Should still calculate valid angle
        self.assertGreaterEqual(angle, 0)
        self.assertLessEqual(angle, 180)


if __name__ == '__main__':
    unittest.main(verbosity=2)
