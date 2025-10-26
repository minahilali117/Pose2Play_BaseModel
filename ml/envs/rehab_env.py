"""
Rehabilitation Exercise Gym Environment for Reinforcement Learning

The RL agent learns to:
1. Adjust exercise difficulty (target angle)
2. Recommend rest breaks
3. Provide encouragement
4. Maximize user performance while preventing fatigue
"""

import gymnasium as gym
from gymnasium import spaces
import numpy as np
from typing import Dict, Tuple, Optional
import pandas as pd


class RehabExerciseEnv(gym.Env):
    """
    Custom Gym environment for rehabilitation exercise optimization
    
    State Space:
        - Recent performance (last 10 reps): angles achieved
        - Consistency score (0-1)
        - Fatigue indicator (0-1)
        - Session duration (seconds)
        - Current difficulty level (target angle)
        - User baseline ability
        - Streak days
        
    Action Space:
        - 0: Decrease difficulty by 5° (make easier)
        - 1: Maintain current difficulty
        - 2: Increase difficulty by 5° (make harder)
        - 3: Suggest rest break
        - 4: Provide encouragement boost
        
    Reward Function:
        +10: Successful rep completion
        +20: Perfect form (within ±3° of target)
        +50: 5 consecutive good reps
        -10: Failed rep (couldn't reach target)
        -20: User quits session (fatigue)
        +100: Personal best achieved
        -5: Making exercise too easy (not challenging)
        -5: Making exercise too hard (user struggling)
    """
    
    metadata = {'render.modes': ['human']}
    
    def __init__(self, user_data: Optional[pd.DataFrame] = None):
        super(RehabExerciseEnv, self).__init__()
        
        # Load user performance data (from dataset)
        self.user_data = user_data
        
        # Action space: 5 discrete actions
        self.action_space = spaces.Discrete(5)
        
        # State space: 20-dimensional continuous
        self.observation_space = spaces.Box(
            low=np.array([
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # Last 10 rep angles (normalized 0-180)
                0,  # Consistency score (0-1)
                0,  # Fatigue indicator (0-1)
                0,  # Session duration (0-3600 seconds)
                60,  # Current target angle (60-120 degrees)
                60,  # User baseline ability (60-120)
                0,  # Streak days (0-100)
                0,  # Reps completed this session (0-50)
                0,  # Success rate last 10 reps (0-1)
                0,  # Average form quality (0-1)
                0   # Time since last rest (0-600 seconds)
            ]),
            high=np.array([
                180, 180, 180, 180, 180, 180, 180, 180, 180, 180,
                1.0,
                1.0,
                3600,
                120,
                120,
                100,
                50,
                1.0,
                1.0,
                600
            ]),
            dtype=np.float32
        )
        
        # Environment state
        self.reset()
    
    def reset(self, seed: Optional[int] = None, options: Optional[Dict] = None) -> Tuple[np.ndarray, Dict]:
        """Reset environment to initial state
        
        Args:
            seed: Random seed for reproducibility
            options: Additional reset options
            
        Returns:
            observation: Initial state
            info: Additional information
        """
        # Set seed for reproducibility
        if seed is not None:
            np.random.seed(seed)
        
        # Initialize user profile (random or from dataset)
        self.user_baseline = np.random.uniform(80, 110)  # Baseline ability
        self.current_target = self.user_baseline + 5  # Start slightly challenging
        
        # Session state
        self.rep_history = []  # List of achieved angles
        self.reps_completed = 0
        self.session_duration = 0
        self.fatigue = 0.0
        self.consecutive_successes = 0
        self.consecutive_failures = 0
        self.rest_timer = 0
        self.streak_days = 0
        
        # Performance tracking
        self.session_quality = []
        self.personal_best = self.user_baseline
        
        return self._get_state(), {}
    
    def _get_state(self) -> np.ndarray:
        """Construct current state vector"""
        # Last 10 rep angles (pad with zeros if < 10)
        last_10_reps = self.rep_history[-10:] if self.rep_history else []
        last_10_reps = last_10_reps + [0] * (10 - len(last_10_reps))
        
        # Normalize angles to 0-180
        last_10_reps = np.array(last_10_reps) / 180.0
        
        # Consistency score (std dev of last 10 reps)
        if len(self.rep_history) >= 3:
            consistency = 1.0 - min(np.std(self.rep_history[-10:]) / 30.0, 1.0)
        else:
            consistency = 0.5
        
        # Success rate
        if len(self.rep_history) >= 1:
            recent_success = np.mean([
                1.0 if abs(angle - self.current_target) <= 10 else 0.0
                for angle in self.rep_history[-10:]
            ])
        else:
            recent_success = 0.5
        
        # Average form quality
        avg_quality = np.mean(self.session_quality) if self.session_quality else 0.5
        
        state = np.concatenate([
            last_10_reps,
            [consistency],
            [self.fatigue],
            [self.session_duration / 3600.0],
            [self.current_target / 180.0],
            [self.user_baseline / 180.0],
            [self.streak_days / 100.0],
            [self.reps_completed / 50.0],
            [recent_success],
            [avg_quality],
            [self.rest_timer / 600.0]
        ])
        
        return state.astype(np.float32)
    
    def step(self, action: int) -> Tuple[np.ndarray, float, bool, bool, Dict]:
        """
        Execute one step in the environment
        
        Args:
            action: 0=decrease difficulty, 1=maintain, 2=increase, 3=rest, 4=encourage
            
        Returns:
            state, reward, terminated, truncated, info
        """
        reward = 0
        terminated = False
        truncated = False
        info = {}
        
        # Apply action
        action_taken = self._apply_action(action)
        info['action'] = action_taken
        
        # Simulate user performing a rep (unless resting)
        if action != 3:  # Not resting
            achieved_angle, quality = self._simulate_rep()
            
            self.rep_history.append(achieved_angle)
            self.session_quality.append(quality)
            self.reps_completed += 1
            self.rest_timer += 10  # 10 seconds per rep
            
            # Calculate reward
            rep_reward = self._calculate_rep_reward(achieved_angle, quality)
            reward += rep_reward
            
            info['achieved_angle'] = achieved_angle
            info['quality'] = quality
            info['rep_reward'] = rep_reward
            
            # Update fatigue
            self._update_fatigue()
        else:
            # Resting - recover fatigue
            self.fatigue = max(0, self.fatigue - 0.2)
            self.rest_timer = 0
            reward += 5  # Small reward for smart resting
            info['action_detail'] = 'rest_taken'
        
        # Check termination conditions
        if self.reps_completed >= 20:
            terminated = True
            reward += 100  # Bonus for completing session
            info['termination'] = 'session_complete'
        elif self.fatigue >= 0.9:
            terminated = True
            reward -= 50  # Penalty for exhausting user
            info['termination'] = 'fatigue_quit'
        elif self.consecutive_failures >= 5:
            terminated = True
            reward -= 30  # Penalty for too many failures
            info['termination'] = 'frustration_quit'
        
        # Update session duration
        self.session_duration += 10
        
        # Get next state
        state = self._get_state()
        
        info['current_target'] = self.current_target
        info['fatigue'] = self.fatigue
        info['consecutive_successes'] = self.consecutive_successes
        
        return state, reward, terminated, truncated, info
    
    def _apply_action(self, action: int) -> str:
        """Apply RL agent's action"""
        if action == 0:  # Decrease difficulty
            self.current_target = min(self.current_target + 5, 120)
            return 'decrease_difficulty'
        elif action == 1:  # Maintain
            return 'maintain_difficulty'
        elif action == 2:  # Increase difficulty
            self.current_target = max(self.current_target - 5, 60)
            return 'increase_difficulty'
        elif action == 3:  # Rest
            return 'rest_break'
        elif action == 4:  # Encourage
            # Encouragement slightly reduces fatigue
            self.fatigue = max(0, self.fatigue - 0.05)
            return 'encouragement'
        
        return 'unknown'
    
    def _simulate_rep(self) -> Tuple[float, float]:
        """
        Simulate user performing a rep
        
        Returns:
            achieved_angle: Angle user achieved (degrees)
            quality: Form quality score (0-1)
        """
        # Base ability with noise
        noise = np.random.normal(0, 5)
        
        # Fatigue affects performance
        fatigue_penalty = self.fatigue * 10
        
        # Difficulty affects success probability
        difficulty_factor = abs(self.current_target - self.user_baseline)
        
        # Achieved angle
        achieved = self.user_baseline - noise + fatigue_penalty + (difficulty_factor * 0.3)
        achieved = np.clip(achieved, 60, 120)
        
        # Quality based on proximity to target
        error = abs(achieved - self.current_target)
        quality = max(0, 1.0 - (error / 20.0))  # 20° tolerance
        
        return achieved, quality
    
    def _calculate_rep_reward(self, achieved_angle: float, quality: float) -> float:
        """Calculate reward for a single rep"""
        reward = 0
        
        error = abs(achieved_angle - self.current_target)
        
        # Base reward for attempting
        reward += 5
        
        # Reward for accuracy
        if error <= 3:  # Perfect form
            reward += 20
            self.consecutive_successes += 1
            self.consecutive_failures = 0
        elif error <= 10:  # Good form
            reward += 10
            self.consecutive_successes += 1
            self.consecutive_failures = 0
        else:  # Missed target
            reward -= 10
            self.consecutive_successes = 0
            self.consecutive_failures += 1
        
        # Bonus for consistency
        if self.consecutive_successes >= 5:
            reward += 50
            self.consecutive_successes = 0  # Reset
        
        # Personal best
        if achieved_angle < self.personal_best:
            self.personal_best = achieved_angle
            reward += 100
        
        # Penalty for making it too easy (not challenging user)
        if self.current_target > self.user_baseline + 15:
            reward -= 5
        
        # Penalty for making it too hard (user can't reach)
        if error > 20:
            reward -= 5
        
        return reward
    
    def _update_fatigue(self):
        """Update user fatigue based on session progress"""
        # Fatigue increases with reps
        self.fatigue += 0.02
        
        # Fatigue increases faster with poor form
        if self.session_quality:
            avg_quality = np.mean(self.session_quality[-5:])
            if avg_quality < 0.5:
                self.fatigue += 0.03
        
        # Fatigue increases if no rest
        if self.rest_timer > 120:  # 2 minutes without rest
            self.fatigue += 0.05
        
        # Cap fatigue
        self.fatigue = min(self.fatigue, 1.0)
    
    def render(self, mode='human'):
        """Render environment state (for debugging)"""
        if mode == 'human':
            print(f"\n{'='*50}")
            print(f"Session Progress: Rep {self.reps_completed}/20")
            print(f"Target Angle: {self.current_target:.1f}°")
            print(f"User Baseline: {self.user_baseline:.1f}°")
            print(f"Fatigue: {self.fatigue:.2f}")
            print(f"Consecutive Successes: {self.consecutive_successes}")
            
            if self.rep_history:
                print(f"Last Rep: {self.rep_history[-1]:.1f}°")
                print(f"Average Quality: {np.mean(self.session_quality):.2f}")
            
            print(f"{'='*50}")


if __name__ == '__main__':
    # Test environment
    env = RehabExerciseEnv()
    
    print("🏋️ Testing Rehabilitation Environment\n")
    
    # Test random policy
    state = env.reset()
    total_reward = 0
    
    for step in range(25):
        # Random action
        action = env.action_space.sample()
        
        state, reward, done, info = env.step(action)
        total_reward += reward
        
        if step % 5 == 0:
            env.render()
        
        if done:
            print(f"\n✅ Episode finished!")
            print(f"   Total reward: {total_reward:.1f}")
            print(f"   Termination: {info.get('termination', 'unknown')}")
            break
    
    print("\n✅ Environment test complete!")
