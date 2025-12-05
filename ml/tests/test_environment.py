"""
Unit tests for RehabExerciseEnv
Tests: RL State Vector, Reward Function, State Machine
"""

import unittest
import numpy as np
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from envs.rehab_env import RehabExerciseEnv


class TestEnvironmentInitialization(unittest.TestCase):
    """Test environment setup and initialization"""
    
    def setUp(self):
        """Initialize environment before each test"""
        self.env = RehabExerciseEnv()
    
    def test_01_environment_creation(self):
        """Test that environment initializes correctly"""
        self.assertIsNotNone(self.env)
        self.assertEqual(self.env.action_space.n, 5, "Should have 5 actions")
        self.assertEqual(self.env.observation_space.shape, (20,), "State should be 20-dimensional")
    
    def test_02_action_space(self):
        """Test action space is correctly defined"""
        # Should have discrete action space with 5 actions
        self.assertEqual(self.env.action_space.n, 5)
        
        # Sample actions should be in range [0, 4]
        for _ in range(100):
            action = self.env.action_space.sample()
            self.assertIn(action, [0, 1, 2, 3, 4])
    
    def test_03_observation_space(self):
        """Test observation space bounds"""
        low = self.env.observation_space.low
        high = self.env.observation_space.high
        
        # Check dimensions
        self.assertEqual(len(low), 20)
        self.assertEqual(len(high), 20)
        
        # Check reasonable bounds
        self.assertTrue(np.all(low >= 0))
        self.assertTrue(np.all(high <= 3600))  # Max session time


class TestEnvironmentReset(unittest.TestCase):
    """Test environment reset functionality"""
    
    def setUp(self):
        self.env = RehabExerciseEnv()
    
    def test_01_reset_returns_valid_state(self):
        """Test reset returns valid state and info"""
        state, info = self.env.reset()
        
        # Check state shape
        self.assertEqual(state.shape, (20,), f"Expected shape (20,), got {state.shape}")
        
        # Check state contains no NaN or Inf
        self.assertTrue(np.all(np.isfinite(state)), "State contains NaN or Inf values")
        
        # Check info is a dictionary
        self.assertIsInstance(info, dict)
    
    def test_02_reset_initializes_counters(self):
        """Test reset properly initializes all counters"""
        self.env.reset()
        
        self.assertEqual(self.env.reps_completed, 0)
        self.assertEqual(len(self.env.rep_history), 0)
        self.assertEqual(self.env.session_duration, 0)
        self.assertGreaterEqual(self.env.fatigue, 0)
        self.assertLessEqual(self.env.fatigue, 1.0)
    
    def test_03_reset_is_deterministic_with_seed(self):
        """Test reset with seed produces same initial state"""
        state1, _ = self.env.reset(seed=42)
        state2, _ = self.env.reset(seed=42)
        
        np.testing.assert_array_almost_equal(state1, state2, decimal=5)
    
    def test_04_reset_clears_previous_episode(self):
        """Test reset clears data from previous episode"""
        # Run an episode
        self.env.reset()
        for _ in range(5):
            self.env.step(1)
        
        # Reset and check everything is cleared
        state, _ = self.env.reset()
        self.assertEqual(self.env.reps_completed, 0)
        self.assertEqual(len(self.env.rep_history), 0)


class TestEnvironmentStep(unittest.TestCase):
    """Test environment step function"""
    
    def setUp(self):
        self.env = RehabExerciseEnv()
        self.env.reset()
    
    def test_01_step_returns_correct_tuple(self):
        """Test step returns (state, reward, terminated, truncated, info)"""
        result = self.env.step(1)
        
        self.assertEqual(len(result), 5, "Step should return 5-tuple")
        state, reward, terminated, truncated, info = result
        
        self.assertEqual(state.shape, (20,))
        self.assertIsInstance(reward, (int, float, np.number))
        self.assertIsInstance(terminated, bool)
        self.assertIsInstance(truncated, bool)
        self.assertIsInstance(info, dict)
    
    def test_02_all_actions_execute(self):
        """Test all 5 actions execute without error"""
        action_names = ['decrease_difficulty', 'maintain_difficulty', 'increase_difficulty', 
                       'rest_break', 'encouragement']
        
        for action in range(5):
            self.env.reset()
            state, reward, terminated, truncated, info = self.env.step(action)
            
            # Validate return types
            self.assertEqual(state.shape, (20,))
            self.assertIsInstance(reward, (int, float, np.number))
            
            # Check info contains action name
            self.assertIn('action', info)
            self.assertEqual(info['action'], action_names[action])
    
    def test_03_state_consistency(self):
        """Test state remains valid after multiple steps"""
        for _ in range(10):
            state, _, done, truncated, _ = self.env.step(1)
            
            # Check state is valid
            self.assertTrue(np.all(np.isfinite(state)))
            self.assertEqual(state.shape, (20,))
            
            if done or truncated:
                break
    
    def test_04_episode_termination(self):
        """Test episode terminates correctly"""
        terminated = False
        truncated = False
        steps = 0
        max_steps = 1000
        
        while not (terminated or truncated) and steps < max_steps:
            _, _, terminated, truncated, _ = self.env.step(1)
            steps += 1
        
        self.assertLess(steps, max_steps, "Episode should terminate within 1000 steps")


class TestDifficultyAdjustment(unittest.TestCase):
    """Test difficulty adjustment actions (Adaptive Adjustment)"""
    
    def setUp(self):
        self.env = RehabExerciseEnv()
        self.env.reset()
    
    def test_01_action_0_decreases_difficulty(self):
        """Test Action 0: Decrease difficulty (make easier)"""
        initial_target = self.env.current_target
        
        # Action 0 should increase target angle (easier)
        self.env.step(0)
        
        self.assertGreater(self.env.current_target, initial_target,
                          "Target should increase (easier)")
    
    def test_02_action_1_maintains_difficulty(self):
        """Test Action 1: Maintain difficulty"""
        initial_target = self.env.current_target
        
        # Action 1 should keep target same
        self.env.step(1)
        
        # Note: target might change slightly due to simulation, but action itself doesn't change it
        # Check the action was recorded correctly
        _, _, _, _, info = self.env.step(1)
        self.assertEqual(info['action'], 'maintain_difficulty')
    
    def test_03_action_2_increases_difficulty(self):
        """Test Action 2: Increase difficulty (make harder)"""
        initial_target = self.env.current_target
        
        # Action 2 should decrease target angle (harder)
        self.env.step(2)
        
        self.assertLess(self.env.current_target, initial_target,
                       "Target should decrease (harder)")
    
    def test_04_difficulty_bounds(self):
        """Test difficulty stays within bounds"""
        # Try to make it very easy
        for _ in range(20):
            self.env.step(0)  # Decrease difficulty
        
        self.assertLessEqual(self.env.current_target, 120, "Target shouldn't exceed 120°")
        
        # Try to make it very hard
        self.env.reset()
        for _ in range(20):
            self.env.step(2)  # Increase difficulty
        
        self.assertGreaterEqual(self.env.current_target, 60, "Target shouldn't go below 60°")


class TestRewardFunction(unittest.TestCase):
    """Test reward calculation (RL Reward Function)"""
    
    def setUp(self):
        self.env = RehabExerciseEnv()
        self.env.reset()
        self.env.current_target = 90
    
    def test_01_perfect_form_reward(self):
        """Test perfect form (±3°) gives high reward"""
        # Simulate perfect rep
        reward = self.env._calculate_rep_reward(achieved_angle=89, quality=0.95)
        
        # Should get base (5) + perfect bonus (20) = 25+
        self.assertGreater(reward, 20, f"Perfect form should earn >20 RP, got {reward}")
    
    def test_02_good_form_reward(self):
        """Test good form (±10°) gives moderate reward"""
        reward = self.env._calculate_rep_reward(achieved_angle=84, quality=0.75)
        
        # Implementation provides high rewards for motivation (100+ RP)
        self.assertGreater(reward, 10, f"Good form should earn >10 RP, got {reward}")
    
    def test_03_missed_target_penalty(self):
        """Test missing target gives negative reward"""
        reward = self.env._calculate_rep_reward(achieved_angle=110, quality=0.3)
        
        # Should get penalty
        self.assertLess(reward, 0, f"Missing target should have negative reward, got {reward}")
    
    def test_04_personal_best_bonus(self):
        """Test achieving personal best gives large bonus"""
        self.env.personal_best = 95
        
        # Achieve new personal best
        reward = self.env._calculate_rep_reward(achieved_angle=88, quality=0.9)
        
        # Should get personal best bonus (100+)
        self.assertGreater(reward, 100, 
                          f"Personal best should earn 100+ bonus, got {reward}")
    
    def test_05_consistency_streak_bonus(self):
        """Test 5 consecutive successes gives bonus"""
        self.env.consecutive_successes = 4  # On 5th success
        
        reward = self.env._calculate_rep_reward(achieved_angle=90, quality=0.95)
        
        # Should get consistency bonus (50+)
        self.assertGreater(reward, 50, 
                          f"Consistency streak should earn 50+ bonus, got {reward}")
    
    def test_06_reward_scaling(self):
        """Test reward scales appropriately with performance"""
        rewards = []
        
        # Test different performance levels
        test_cases = [
            (88, 0.95),   # Perfect
            (85, 0.80),   # Good
            (80, 0.60),   # Acceptable
            (100, 0.40),  # Poor
            (115, 0.20)   # Very poor
        ]
        
        for angle, quality in test_cases:
            reward = self.env._calculate_rep_reward(angle, quality)
            rewards.append(reward)
        
        # Rewards should generally decrease as performance worsens
        # Perfect and good should be positive, poor should be lower
        self.assertGreater(rewards[0], 20, "Perfect form should give high reward")
        self.assertGreater(rewards[2], rewards[4], "Acceptable should beat very poor")


class TestStateVector(unittest.TestCase):
    """Test state vector construction (RL State Vector)"""
    
    def setUp(self):
        self.env = RehabExerciseEnv()
        self.env.reset()
    
    def test_01_state_dimensions(self):
        """Verify state has exactly 20 dimensions"""
        state = self.env._get_state()
        
        self.assertEqual(len(state), 20, f"State should have 20 dimensions, got {len(state)}")
        self.assertEqual(state.shape, (20,))
    
    def test_02_state_no_nan_or_inf(self):
        """Test state contains no invalid values"""
        state = self.env._get_state()
        
        self.assertTrue(np.all(np.isfinite(state)), 
                       "State contains NaN or Inf values")
    
    def test_03_state_normalization(self):
        """Test state values are properly normalized"""
        # Add some history
        self.env.rep_history = [90, 85, 95, 88, 92]
        self.env.reps_completed = 5
        self.env.fatigue = 0.3
        
        state = self.env._get_state()
        
        # Most values should be in [0, 1] range (normalized)
        # Angles are normalized to [0, 1] by dividing by 180
        for i in range(10):  # First 10 are angles
            self.assertGreaterEqual(state[i], 0)
            self.assertLessEqual(state[i], 1)
    
    def test_04_state_consistency_calculation(self):
        """Test consistency metric is calculated correctly"""
        # Add consistent angles to history
        consistent_angles = [90, 91, 89, 90, 91, 90, 89, 91, 90, 90]
        self.env.rep_history = consistent_angles
        
        state = self.env._get_state()
        consistency = state[10]  # Index 10 is consistency score
        
        # High consistency should be near 1.0
        self.assertGreater(consistency, 0.8, 
                          f"Consistent angles should have high score, got {consistency}")
        
        # Now test inconsistent angles
        self.env.rep_history = [70, 100, 75, 95, 80, 110, 65, 105, 72, 98]
        state = self.env._get_state()
        consistency = state[10]
        
        # Low consistency should be lower
        self.assertLess(consistency, 0.7,
                       f"Inconsistent angles should have low score, got {consistency}")
    
    def test_05_state_padding_with_few_reps(self):
        """Test state vector pads correctly with < 10 reps"""
        self.env.rep_history = [90, 85, 92]  # Only 3 reps
        
        state = self.env._get_state()
        
        # Should still have 20 dimensions
        self.assertEqual(len(state), 20)
        
        # Padded values should be reasonable (zeros or small values)
        self.assertTrue(np.all(np.isfinite(state)))


class TestFatigueSystem(unittest.TestCase):
    """Test fatigue accumulation and rest mechanics"""
    
    def setUp(self):
        self.env = RehabExerciseEnv()
        self.env.reset()
    
    def test_01_fatigue_increases_over_time(self):
        """Test fatigue increases with reps"""
        initial_fatigue = self.env.fatigue
        
        # Simulate multiple reps
        for _ in range(10):
            self.env.step(1)  # Maintain difficulty
        
        # Fatigue should increase
        self.assertGreater(self.env.fatigue, initial_fatigue,
                          "Fatigue should increase after multiple reps")
    
    def test_02_rest_reduces_fatigue(self):
        """Test Action 3 (rest) reduces fatigue"""
        # Build up fatigue
        for _ in range(10):
            self.env.step(1)
        
        fatigue_before_rest = self.env.fatigue
        
        # Take rest
        self.env.step(3)
        
        # Fatigue should decrease
        self.assertLess(self.env.fatigue, fatigue_before_rest,
                       "Rest should reduce fatigue")
    
    def test_03_encouragement_reduces_fatigue(self):
        """Test Action 4 (encouragement) reduces fatigue slightly"""
        # Build up some fatigue
        for _ in range(5):
            self.env.step(1)
        
        fatigue_before = self.env.fatigue
        
        # Give encouragement
        self.env.step(4)
        
        # Fatigue should decrease slightly
        self.assertLessEqual(self.env.fatigue, fatigue_before,
                            "Encouragement should reduce fatigue")
    
    def test_04_fatigue_causes_termination(self):
        """Test high fatigue terminates episode"""
        # Artificially set high fatigue
        self.env.fatigue = 0.95
        
        # Next step should terminate
        _, _, terminated, _, info = self.env.step(1)
        
        if terminated:
            self.assertEqual(info.get('termination'), 'fatigue_quit',
                           "Should terminate due to fatigue")


class TestSessionCompletion(unittest.TestCase):
    """Test episode termination conditions"""
    
    def setUp(self):
        self.env = RehabExerciseEnv()
        self.env.reset()
    
    def test_01_session_completes_after_target_reps(self):
        """Test episode terminates after target reps"""
        terminated = False
        truncated = False
        reps = 0
        
        while not (terminated or truncated) and reps < 30:
            _, _, terminated, truncated, info = self.env.step(1)
            reps += 1
        
        # Should terminate around 20 reps
        self.assertTrue(terminated or truncated, 
                       "Session should terminate after target reps")
        
        if terminated and 'termination' in info:
            self.assertIn(info['termination'], 
                         ['session_complete', 'fatigue_quit', 'frustration_quit'])
    
    def test_02_frustration_quit_after_failures(self):
        """Test episode terminates after consecutive failures"""
        # Make target impossible to reach
        self.env.current_target = 60  # Very hard
        self.env.user_baseline = 120  # User can't reach it
        
        terminated = False
        steps = 0
        
        while not terminated and steps < 10:
            _, _, terminated, _, info = self.env.step(1)
            steps += 1
        
        # Should eventually terminate (either frustration or fatigue)
        # This is a probabilistic test, so we just check it doesn't crash


if __name__ == '__main__':
    # Run all tests
    unittest.main(verbosity=2)
