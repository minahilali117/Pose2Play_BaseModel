"""
Train Reinforcement Learning Agent for Adaptive Rehabilitation

Uses Deep Q-Network (DQN) to learn optimal difficulty adjustment policy
"""

import os
import numpy as np
import pandas as pd
from pathlib import Path
import json
import matplotlib.pyplot as plt

# RL libraries
from stable_baselines3 import DQN, PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.callbacks import BaseCallback, EvalCallback
from stable_baselines3.common.monitor import Monitor

# Custom environment
import sys
sys.path.append(str(Path(__file__).parent))
from envs.rehab_env import RehabExerciseEnv


class RehabTrainingCallback(BaseCallback):
    """Custom callback for logging training progress"""
    
    def __init__(self, verbose=0):
        super(RehabTrainingCallback, self).__init__(verbose)
        self.episode_rewards = []
        self.episode_lengths = []
        self.current_episode_reward = 0
        self.current_episode_length = 0
    
    def _on_step(self) -> bool:
        self.current_episode_reward += self.locals['rewards'][0]
        self.current_episode_length += 1
        
        # Check if episode done
        if self.locals['dones'][0]:
            self.episode_rewards.append(self.current_episode_reward)
            self.episode_lengths.append(self.current_episode_length)
            
            if len(self.episode_rewards) % 100 == 0:
                avg_reward = np.mean(self.episode_rewards[-100:])
                print(f"Episode {len(self.episode_rewards)}: "
                      f"Avg Reward (last 100): {avg_reward:.2f}")
            
            # Reset
            self.current_episode_reward = 0
            self.current_episode_length = 0
        
        return True


class RehabRLTrainer:
    """Train RL agent for rehabilitation exercise optimization"""
    
    def __init__(self, 
                 data_path: str = None,
                 algorithm: str = 'DQN',
                 output_dir: str = './models'):
        
        self.data_path = Path(data_path) if data_path else None
        self.algorithm = algorithm
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load user data if available
        self.user_data = None
        if self.data_path and self.data_path.exists():
            self.user_data = pd.read_csv(self.data_path)
            print(f"✅ Loaded user data: {len(self.user_data)} samples")
    
    def create_env(self):
        """Create and wrap environment"""
        env = RehabExerciseEnv(user_data=self.user_data)
        env = Monitor(env)
        return env
    
    def train(self, 
              total_timesteps: int = 100000,
              learning_rate: float = 1e-4,
              save_freq: int = 10000):
        """
        Train RL agent
        
        Args:
            total_timesteps: Total training steps
            learning_rate: Learning rate for optimizer
            save_freq: Save model every N steps
        """
        print(f"\n🚀 Training {self.algorithm} agent...")
        print(f"   Timesteps: {total_timesteps}")
        print(f"   Learning rate: {learning_rate}")
        
        # Create environment
        env = self.create_env()
        
        # Create evaluation environment
        eval_env = self.create_env()
        
        # Initialize agent
        if self.algorithm == 'DQN':
            model = DQN(
                "MlpPolicy",
                env,
                learning_rate=learning_rate,
                buffer_size=50000,
                learning_starts=1000,
                batch_size=64,
                tau=0.005,
                gamma=0.99,
                train_freq=4,
                target_update_interval=1000,
                exploration_fraction=0.3,
                exploration_initial_eps=1.0,
                exploration_final_eps=0.05,
                verbose=1,
                tensorboard_log=str(self.output_dir / 'tensorboard')
            )
        elif self.algorithm == 'PPO':
            model = PPO(
                "MlpPolicy",
                env,
                learning_rate=learning_rate,
                n_steps=2048,
                batch_size=64,
                n_epochs=10,
                gamma=0.99,
                gae_lambda=0.95,
                clip_range=0.2,
                verbose=1,
                tensorboard_log=str(self.output_dir / 'tensorboard')
            )
        else:
            raise ValueError(f"Unknown algorithm: {self.algorithm}")
        
        # Callbacks
        training_callback = RehabTrainingCallback()
        
        eval_callback = EvalCallback(
            eval_env,
            best_model_save_path=str(self.output_dir / 'best_model'),
            log_path=str(self.output_dir / 'eval_logs'),
            eval_freq=5000,
            deterministic=True,
            render=False
        )
        
        # Train
        model.learn(
            total_timesteps=total_timesteps,
            callback=[training_callback, eval_callback]
        )
        
        # Save final model
        model_path = self.output_dir / f'{self.algorithm}_rehab_final.zip'
        model.save(str(model_path))
        print(f"\n✅ Model saved to: {model_path}")
        
        # Save training metrics
        self._save_training_metrics(training_callback)
        
        return model
    
    def _save_training_metrics(self, callback: RehabTrainingCallback):
        """Save training metrics and plot"""
        metrics = {
            'episode_rewards': [float(r) for r in callback.episode_rewards],
            'episode_lengths': [float(l) for l in callback.episode_lengths]
        }
        
        # Save to JSON
        metrics_path = self.output_dir / 'training_metrics.json'
        with open(metrics_path, 'w') as f:
            json.dump(metrics, f, indent=2)
        
        # Plot rewards
        plt.figure(figsize=(12, 5))
        
        plt.subplot(1, 2, 1)
        plt.plot(callback.episode_rewards, alpha=0.3)
        
        # Moving average
        if len(callback.episode_rewards) > 100:
            moving_avg = pd.Series(callback.episode_rewards).rolling(100).mean()
            plt.plot(moving_avg, linewidth=2, label='100-episode average')
        
        plt.xlabel('Episode')
        plt.ylabel('Total Reward')
        plt.title('Training Rewards')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plt.subplot(1, 2, 2)
        plt.plot(callback.episode_lengths)
        plt.xlabel('Episode')
        plt.ylabel('Episode Length')
        plt.title('Episode Lengths')
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plot_path = self.output_dir / 'training_plot.png'
        plt.savefig(plot_path, dpi=150)
        print(f"📊 Training plot saved to: {plot_path}")
    
    def evaluate(self, model_path: str, n_episodes: int = 100):
        """Evaluate trained model"""
        print(f"\n📊 Evaluating model: {model_path}")
        
        # Load model
        if self.algorithm == 'DQN':
            model = DQN.load(model_path)
        elif self.algorithm == 'PPO':
            model = PPO.load(model_path)
        
        # Create environment
        env = self.create_env()
        
        # Evaluate
        episode_rewards = []
        episode_infos = []
        
        for ep in range(n_episodes):
            state, _ = env.reset()  # Gymnasium API returns (obs, info)
            done = False
            total_reward = 0
            
            while not done:
                action, _ = model.predict(state, deterministic=True)
                state, reward, terminated, truncated, info = env.step(action)  # Gymnasium API returns 5 values
                done = terminated or truncated
                total_reward += reward
            
            episode_rewards.append(total_reward)
            episode_infos.append(info)
        
        # Statistics
        results = {
            'mean_reward': float(np.mean(episode_rewards)),
            'std_reward': float(np.std(episode_rewards)),
            'min_reward': float(np.min(episode_rewards)),
            'max_reward': float(np.max(episode_rewards)),
            'termination_reasons': {
                'session_complete': int(sum(1 for info in episode_infos if info.get('termination') == 'session_complete')),
                'fatigue_quit': int(sum(1 for info in episode_infos if info.get('termination') == 'fatigue_quit')),
                'frustration_quit': int(sum(1 for info in episode_infos if info.get('termination') == 'frustration_quit'))
            }
        }
        
        print(f"\n✅ Evaluation Results (n={n_episodes}):")
        print(f"   Mean Reward: {results['mean_reward']:.2f} ± {results['std_reward']:.2f}")
        print(f"   Min/Max: {results['min_reward']:.2f} / {results['max_reward']:.2f}")
        print(f"   Termination Reasons:")
        for reason, count in results['termination_reasons'].items():
            print(f"      {reason}: {count} ({count/n_episodes*100:.1f}%)")
        
        # Save results
        results_path = self.output_dir / 'evaluation_results.json'
        with open(results_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        return results
    
    def export_for_deployment(self, model_path: str):
        """Export model for web deployment (TensorFlow.js)"""
        print(f"\n📦 Exporting model for deployment...")
        
        # Load model
        if self.algorithm == 'DQN':
            model = DQN.load(model_path)
        elif self.algorithm == 'PPO':
            model = PPO.load(model_path)
        
        # Extract policy network
        policy = model.policy
        
        # Save policy separately
        policy_path = self.output_dir / 'policy_network'
        policy_path.mkdir(exist_ok=True)
        
        # TODO: Convert to ONNX or TensorFlow.js format
        # This requires additional libraries:
        # pip install onnx onnxruntime tensorflowjs
        
        print(f"⚠️  Manual conversion required:")
        print(f"   1. Install: pip install onnx tensorflowjs")
        print(f"   2. Convert policy to ONNX")
        print(f"   3. Convert ONNX to TensorFlow.js")
        print(f"   4. Deploy to demo/models/")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Train RL agent for rehabilitation')
    parser.add_argument('--algorithm', type=str, default='DQN', choices=['DQN', 'PPO'],
                        help='RL algorithm to use')
    parser.add_argument('--timesteps', type=int, default=100000,
                        help='Total training timesteps')
    parser.add_argument('--lr', type=float, default=1e-4,
                        help='Learning rate')
    parser.add_argument('--data', type=str, default=None,
                        help='Path to processed user data CSV')
    parser.add_argument('--output', type=str, default='./models',
                        help='Output directory for models')
    parser.add_argument('--mode', type=str, default='train', choices=['train', 'eval'],
                        help='Train or evaluate mode')
    parser.add_argument('--model', type=str, default=None,
                        help='Path to model for evaluation')
    
    args = parser.parse_args()
    
    # Create trainer
    trainer = RehabRLTrainer(
        data_path=args.data,
        algorithm=args.algorithm,
        output_dir=args.output
    )
    
    if args.mode == 'train':
        # Train model
        model = trainer.train(
            total_timesteps=args.timesteps,
            learning_rate=args.lr
        )
        
        print("\n✅ Training complete!")
        print(f"📁 Models saved to: {args.output}")
        
    elif args.mode == 'eval':
        if not args.model:
            print("❌ Error: --model required for evaluation")
        else:
            # Evaluate model
            trainer.evaluate(args.model, n_episodes=100)
