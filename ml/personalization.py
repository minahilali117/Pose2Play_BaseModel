"""
Rehabilitation Personalization Engine

Maintains per-user profiles and adaptively adjusts target ROM based on:
  - User's baseline ROM (first few sessions)
  - Best ROM achieved so far
  - Exponential moving average (EMA) of quality scores
  - Global dataset statistics

Strategy:
  - Start conservative (user's baseline + small increment)
  - Increase target as quality improves
  - Cap target at global max ROM from training data
  - Use EMA to smooth quality variations and prevent over-aggressive targets
"""

from typing import Dict, Optional
import numpy as np


class RehabPersonalizer:
    """
    Adaptive personalization engine for rehabilitation exercises.
    
    Maintains per-user state:
      - baseline_rom: Initial ROM capability (average of first N reps)
      - best_rom: Maximum ROM achieved across all sessions
      - ema_quality: Exponential moving average of quality scores
      - rep_count: Total reps completed
      - target_rom: Current target ROM for next rep
    
    Logic:
      1. Establish baseline from first 5 reps
      2. Set target = baseline + base_increment
      3. Adjust target based on ema_quality:
         - High quality (>0.8) → increase target slightly
         - Medium quality (0.5-0.8) → maintain target
         - Low quality (<0.5) → decrease target slightly
      4. Never exceed global_max_rom or best_rom + max_extra
    """
    
    def __init__(self, 
                 global_max_rom: float,
                 base_increment_deg: float = 5.0,
                 max_extra_deg: float = 30.0,
                 ema_alpha: float = 0.3,
                 baseline_reps: int = 5):
        """
        Args:
          global_max_rom: Maximum ROM observed in training dataset (degrees)
          base_increment_deg: Initial increment above baseline for target (degrees)
          max_extra_deg: Maximum allowed increment above user's best ROM (degrees)
          ema_alpha: Smoothing factor for quality EMA (0=no update, 1=replace)
          baseline_reps: Number of reps to establish baseline ROM
        """
        self.global_max_rom = global_max_rom
        self.base_increment_deg = base_increment_deg
        self.max_extra_deg = max_extra_deg
        self.ema_alpha = ema_alpha
        self.baseline_reps = baseline_reps
        
        # Per-user profiles
        # Structure: user_id -> {baseline_rom, best_rom, ema_quality, rep_count, target_rom, rom_history}
        self.user_profiles: Dict[str, Dict] = {}
    
    def _init_user_profile(self, user_id: str) -> Dict:
        """Initialize a new user profile."""
        return {
            'baseline_rom': None,          # Established after baseline_reps
            'best_rom': 0.0,               # Maximum ROM achieved
            'ema_quality': 0.5,            # Start neutral
            'rep_count': 0,                # Total reps completed
            'target_rom': None,            # Current target (set after baseline)
            'rom_history': []              # List of recent ROMs for baseline calculation
        }
    
    def update_and_get_target(self, 
                              user_id: str, 
                              rep_rom: float, 
                              quality_score: float) -> float:
        """
        Update user profile with new rep data and return personalized target ROM.
        
        Args:
          user_id: Unique identifier for user
          rep_rom: Range of motion achieved in this rep (degrees)
          quality_score: Movement quality score from LSTM model [0, 1]
        
        Returns:
          target_rom: Personalized target ROM for next rep (degrees)
        """
        # Get or create user profile
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = self._init_user_profile(user_id)
        
        profile = self.user_profiles[user_id]
        
        # Update rep count
        profile['rep_count'] += 1
        
        # Update best ROM
        if rep_rom > profile['best_rom']:
            profile['best_rom'] = rep_rom
        
        # Update EMA quality
        if profile['ema_quality'] is None:
            profile['ema_quality'] = quality_score
        else:
            profile['ema_quality'] = (
                self.ema_alpha * quality_score + 
                (1 - self.ema_alpha) * profile['ema_quality']
            )
        
        # Establish baseline ROM (average of first N reps)
        if profile['baseline_rom'] is None:
            profile['rom_history'].append(rep_rom)
            
            if len(profile['rom_history']) >= self.baseline_reps:
                profile['baseline_rom'] = np.mean(profile['rom_history'])
                # Set initial target
                profile['target_rom'] = min(
                    profile['baseline_rom'] + self.base_increment_deg,
                    self.global_max_rom
                )
                print(f"[Personalizer] User {user_id}: Baseline ROM established at {profile['baseline_rom']:.1f}°")
                print(f"[Personalizer] Initial target: {profile['target_rom']:.1f}°")
        
        # Adjust target based on quality and performance
        if profile['target_rom'] is not None:
            # Calculate quality-based adjustment
            ema_quality = profile['ema_quality']
            
            if ema_quality > 0.8:
                # High quality → increase target (user ready for more challenge)
                adjustment = 2.0
            elif ema_quality > 0.6:
                # Good quality → small increase
                adjustment = 1.0
            elif ema_quality > 0.4:
                # Medium quality → maintain
                adjustment = 0.0
            else:
                # Low quality → decrease target (too challenging)
                adjustment = -2.0
            
            # Apply adjustment
            new_target = profile['target_rom'] + adjustment
            
            # Constrain target
            # 1. Not below baseline
            new_target = max(new_target, profile['baseline_rom'])
            
            # 2. Not too far above best ROM
            max_allowed = profile['best_rom'] + self.max_extra_deg
            new_target = min(new_target, max_allowed)
            
            # 3. Not above global max
            new_target = min(new_target, self.global_max_rom)
            
            profile['target_rom'] = new_target
        
        # If still in baseline phase, return conservative estimate
        if profile['target_rom'] is None:
            return min(rep_rom + self.base_increment_deg, self.global_max_rom)
        
        return profile['target_rom']
    
    def get_user_stats(self, user_id: str) -> Optional[Dict]:
        """
        Get current stats for a user.
        
        Returns:
          dict with keys: baseline_rom, best_rom, ema_quality, rep_count, target_rom
          or None if user not found
        """
        if user_id not in self.user_profiles:
            return None
        
        profile = self.user_profiles[user_id]
        return {
            'baseline_rom': profile['baseline_rom'],
            'best_rom': profile['best_rom'],
            'ema_quality': profile['ema_quality'],
            'rep_count': profile['rep_count'],
            'target_rom': profile['target_rom']
        }
    
    def reset_user(self, user_id: str):
        """Reset a user's profile (useful for testing or new training cycle)."""
        if user_id in self.user_profiles:
            del self.user_profiles[user_id]


# ============================================================
# Testing / Simulation
# ============================================================

if __name__ == '__main__':
    # Simulate personalization over multiple reps
    print("Testing RehabPersonalizer...")
    
    # Create personalizer with typical settings
    personalizer = RehabPersonalizer(
        global_max_rom=150.0,
        base_increment_deg=5.0,
        max_extra_deg=30.0,
        ema_alpha=0.3,
        baseline_reps=5
    )
    
    # Simulate a user performing reps with improving quality
    user_id = "test_user_001"
    
    # Simulate 20 reps
    simulated_reps = [
        # Baseline phase (reps 1-5): Low ROM, learning
        (80.0, 0.5),
        (82.0, 0.55),
        (85.0, 0.6),
        (83.0, 0.58),
        (87.0, 0.65),
        
        # Improvement phase (reps 6-15): Increasing ROM and quality
        (90.0, 0.7),
        (92.0, 0.75),
        (95.0, 0.78),
        (98.0, 0.82),
        (100.0, 0.85),
        (102.0, 0.87),
        (105.0, 0.88),
        (107.0, 0.90),
        (110.0, 0.92),
        (112.0, 0.91),
        
        # Plateau phase (reps 16-20): Maintaining high quality
        (115.0, 0.93),
        (113.0, 0.91),
        (116.0, 0.94),
        (118.0, 0.95),
        (120.0, 0.96),
    ]
    
    print(f"\n{'Rep':<5} {'ROM':<8} {'Quality':<10} {'EMA Q':<10} {'Target':<10} {'Best':<8}")
    print("-" * 60)
    
    for rep_num, (rom, quality) in enumerate(simulated_reps, 1):
        target = personalizer.update_and_get_target(user_id, rom, quality)
        stats = personalizer.get_user_stats(user_id)
        
        print(f"{rep_num:<5} {rom:<8.1f} {quality:<10.2f} "
              f"{stats['ema_quality']:<10.2f} {target:<10.1f} {stats['best_rom']:<8.1f}")
    
    print("\n✅ Personalization test complete!")
    print("\nFinal user stats:")
    final_stats = personalizer.get_user_stats(user_id)
    for key, value in final_stats.items():
        if value is not None:
            print(f"  {key}: {value:.2f}" if isinstance(value, float) else f"  {key}: {value}")
