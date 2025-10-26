"""
Generate training summary and plots from completed DQN training
"""
import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Load training metrics
metrics_path = Path('models/dqn/training_metrics.json')
with open(metrics_path, 'r') as f:
    metrics = json.load(f)

episode_rewards = metrics['episode_rewards']
episode_lengths = metrics['episode_lengths']

print("=" * 60)
print("🎉 TRAINING COMPLETE - RESULTS SUMMARY")
print("=" * 60)
print(f"\nTotal Episodes: {len(episode_rewards)}")
print(f"\nReward Statistics:")
print(f"  Mean Reward: {np.mean(episode_rewards):.1f}")
print(f"  Std Dev: {np.std(episode_rewards):.1f}")
print(f"  Min Reward: {np.min(episode_rewards):.1f}")
print(f"  Max Reward: {np.max(episode_rewards):.1f}")

print(f"\nEpisode Length:")
print(f"  Mean Length: {np.mean(episode_lengths):.1f}")
print(f"  All episodes: {episode_lengths[0]:.0f} steps")

# Calculate moving averages
if len(episode_rewards) >= 100:
    last_100_avg = np.mean(episode_rewards[-100:])
    print(f"\nLast 100 Episodes Avg Reward: {last_100_avg:.1f}")

# Create visualization
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))

# Plot 1: Episode Rewards
ax1.plot(episode_rewards, alpha=0.3, color='blue', label='Episode Reward')
if len(episode_rewards) >= 100:
    moving_avg = np.convolve(episode_rewards, np.ones(100)/100, mode='valid')
    ax1.plot(range(99, len(episode_rewards)), moving_avg, 
             color='red', linewidth=2, label='100-Episode Moving Average')
ax1.set_xlabel('Episode', fontsize=12)
ax1.set_ylabel('Reward', fontsize=12)
ax1.set_title('DQN Training - Episode Rewards', fontsize=14, fontweight='bold')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Plot 2: Reward Distribution
ax2.hist(episode_rewards, bins=50, color='green', alpha=0.7, edgecolor='black')
ax2.axvline(np.mean(episode_rewards), color='red', linestyle='--', 
            linewidth=2, label=f'Mean: {np.mean(episode_rewards):.1f}')
ax2.set_xlabel('Reward', fontsize=12)
ax2.set_ylabel('Frequency', fontsize=12)
ax2.set_title('Reward Distribution', fontsize=14, fontweight='bold')
ax2.legend()
ax2.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('models/dqn/training_plot.png', dpi=150, bbox_inches='tight')
print(f"\n✅ Training plot saved to: models/dqn/training_plot.png")

# Performance analysis
print("\n" + "=" * 60)
print("📊 PERFORMANCE ANALYSIS")
print("=" * 60)

mean_reward = np.mean(episode_rewards)
if mean_reward >= 800:
    print("✅ EXCELLENT: Mean reward > 800 (Target: 400-500)")
    print("   Model learned very effective difficulty adjustment!")
elif mean_reward >= 400:
    print("✅ GOOD: Mean reward in target range (400-500)")
    print("   Model learned good difficulty adjustment.")
elif mean_reward >= 300:
    print("⚠️  ACCEPTABLE: Mean reward slightly below target")
    print("   Consider retraining with adjusted hyperparameters.")
else:
    print("❌ POOR: Mean reward < 300")
    print("   Model needs retraining with different settings.")

print("\n" + "=" * 60)
print("🎯 NEXT STEPS")
print("=" * 60)
print("1. View training plot:")
print("   start models/dqn/training_plot.png")
print("\n2. Test the trained model:")
print("   python train_rl.py --mode eval --algorithm DQN --model ./models/dqn/DQN_rehab_final.zip")
print("\n3. Interactive testing:")
print("   python")
print("   >>> from envs.rehab_env import RehabExerciseEnv")
print("   >>> from stable_baselines3 import DQN")
print("   >>> env = RehabExerciseEnv()")
print("   >>> model = DQN.load('./models/dqn/DQN_rehab_final.zip')")
print("   >>> state, _ = env.reset()")
print("   >>> action, _ = model.predict(state, deterministic=True)")
print("\n" + "=" * 60)
