"""
Training Script for Multi-Exercise LSTM Movement Quality Classifier

Trains a bidirectional LSTM model on UI-PRMD exercises to predict
movement quality (correct vs incorrect form).

Supports:
  - Squat/knee-dominant: m01, m05
  - Hip-dominant: m03, m06  
  - Shoulder: m07, m10

Usage:
  python -m ml.train_lstm

  or from ml/ directory:
  python train_lstm.py
"""

import os
import sys
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split
import numpy as np
from pathlib import Path
import csv
from datetime import datetime
from tqdm.auto import tqdm

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from data.ui_prmd_loader import ShoulderRehabDataset, SEQ_LEN, ANGLE_COLUMN_INDICES
from models.lstm_quality import ShoulderLSTM


# ============================================================
# CONFIGURATION
# ============================================================

# Dataset path - now uses automatic resolution from ui_prmd_loader.py
# No hardcoded paths needed!

# Training hyperparameters
BATCH_SIZE = 16
LEARNING_RATE = 0.001
NUM_EPOCHS = 50
TRAIN_SPLIT = 0.8  # 80% train, 20% validation

# Model hyperparameters
HIDDEN_SIZE = 64
NUM_LAYERS = 2
DROPOUT = 0.3

# Output paths
MODEL_SAVE_PATH = Path(__file__).parent / "models" / "shoulder_lstm_model.pt"
MODEL_SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)

# Log directory
LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Create timestamped log file
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_FILE = LOG_DIR / f"lstm_training_{timestamp}.csv"

# Device
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


# ============================================================
# Training Functions
# ============================================================

def calculate_accuracy(logits: torch.Tensor, labels: torch.Tensor) -> float:
    """Calculate binary classification accuracy."""
    preds = (torch.sigmoid(logits) > 0.5).float()
    correct = (preds == labels).float().sum()
    accuracy = correct / len(labels)
    return accuracy.item()


def train_epoch(model: nn.Module, 
                dataloader: DataLoader, 
                criterion: nn.Module, 
                optimizer: optim.Optimizer,
                device: torch.device,
                epoch: int,
                num_epochs: int) -> tuple:
    """
    Train for one epoch.
    
    Returns:
      (avg_loss, avg_accuracy, num_correct, num_samples)
    """
    model.train()
    
    total_loss = 0.0
    total_correct = 0
    total_samples = 0
    
    # Progress bar for training batches
    pbar = tqdm(dataloader, desc=f"Epoch {epoch}/{num_epochs} [train]", leave=False)
    
    for batch_data in pbar:
        # Unpack batch (now includes movement_id)
        sequences, labels, roms, movement_ids = batch_data
        
        # Move to device
        sequences = sequences.to(device)  # [batch, seq_len, features]
        labels = labels.squeeze().to(device)  # [batch]
        
        batch_size = len(labels)
        
        # Forward pass
        logits = model(sequences)  # [batch]
        loss = criterion(logits, labels)
        
        # Backward pass
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        # Metrics
        preds = (torch.sigmoid(logits) > 0.5).float()
        correct = (preds == labels).float().sum().item()
        
        total_loss += loss.item()
        total_correct += correct
        total_samples += batch_size
        
        # Update progress bar
        pbar.set_postfix({'loss': f'{loss.item():.4f}'})
    
    avg_loss = total_loss / len(dataloader)
    avg_accuracy = total_correct / total_samples
    
    return avg_loss, avg_accuracy, int(total_correct), total_samples


def validate(model: nn.Module, 
            dataloader: DataLoader, 
            criterion: nn.Module,
            device: torch.device,
            epoch: int,
            num_epochs: int) -> tuple:
    """
    Validate model.
    
    Returns:
      (avg_loss, avg_accuracy, num_correct, num_samples)
    """
    model.eval()
    
    total_loss = 0.0
    total_correct = 0
    total_samples = 0
    
    # Progress bar for validation
    pbar = tqdm(dataloader, desc=f"Epoch {epoch}/{num_epochs} [val]  ", leave=False)
    
    with torch.no_grad():
        for batch_data in pbar:
            # Unpack batch (now includes movement_id)
            sequences, labels, roms, movement_ids = batch_data
            
            # Move to device
            sequences = sequences.to(device)
            labels = labels.squeeze().to(device)
            
            batch_size = len(labels)
            
            # Forward pass
            logits = model(sequences)
            loss = criterion(logits, labels)
            
            # Metrics
            preds = (torch.sigmoid(logits) > 0.5).float()
            correct = (preds == labels).float().sum().item()
            
            total_loss += loss.item()
            total_correct += correct
            total_samples += batch_size
            
            # Update progress bar
            pbar.set_postfix({'loss': f'{loss.item():.4f}'})
    
    avg_loss = total_loss / len(dataloader)
    avg_accuracy = total_correct / total_samples
    
    return avg_loss, avg_accuracy, int(total_correct), total_samples


def save_checkpoint(model: nn.Module, 
                   dataset: ShoulderRehabDataset,
                   epoch: int,
                   val_loss: float,
                   val_accuracy: float,
                   filepath: Path):
    """
    Save model checkpoint with metadata.
    
    Saves:
      - Model state dict
      - Input size and sequence length
      - Normalization parameters (mean, std, global_max_rom)
      - Training metadata
    """
    norm_params = dataset.get_normalization_params()
    
    checkpoint = {
        # Model
        'model_state_dict': model.state_dict(),
        'input_size': dataset.sequences[0].shape[1],  # Number of features
        'seq_len': dataset.seq_len,
        'hidden_size': model.hidden_size,
        'num_layers': model.num_layers,
        
        # Normalization parameters (critical for inference)
        'angle_mean': norm_params['angle_mean'].tolist(),
        'angle_std': norm_params['angle_std'].tolist(),
        'global_max_rom': float(norm_params['global_max_rom']),
        
        # Training metadata
        'epoch': epoch,
        'val_loss': val_loss,
        'val_accuracy': val_accuracy,
        'column_indices': ANGLE_COLUMN_INDICES,
        
        # Dataset info
        'num_training_samples': len(dataset),
        'movements': dataset.movements
    }
    
    torch.save(checkpoint, filepath)
    print(f"✅ Checkpoint saved to: {filepath}")


def analyze_dataset_distribution(dataset, train_indices, val_indices):
    """Print per-movement distribution in train/val splits."""
    from collections import Counter
    
    train_movements = [dataset.movement_ids[i] for i in train_indices]
    val_movements = [dataset.movement_ids[i] for i in val_indices]
    
    train_counter = Counter(train_movements)
    val_counter = Counter(val_movements)
    
    print("\nDataset Split by Movement:")
    print(f"  {'Movement':<10} {'Train':<10} {'Val':<10} {'Total':<10}")
    print("  " + "-"*40)
    
    all_movements = sorted(set(train_movements + val_movements))
    for movement in all_movements:
        train_count = train_counter.get(movement, 0)
        val_count = val_counter.get(movement, 0)
        total = train_count + val_count
        print(f"  {movement:<10} {train_count:<10} {val_count:<10} {total:<10}")
    print()


def train():
    """Main training loop."""
    print("="*60)
    print("LSTM Training for Multi-Exercise Movement Quality")
    print("="*60)
    print(f"Device: {DEVICE}")
    print(f"Log file: {LOG_FILE}")
    print()
    
    # Load dataset (uses automatic path resolution)
    print("Loading dataset...")
    try:
        dataset = ShoulderRehabDataset(
            data_root=None,  # Use automatic path resolution
            seq_len=SEQ_LEN,
            column_indices=ANGLE_COLUMN_INDICES,
            normalize=True
        )
    except Exception as e:
        print(f"❌ Error loading dataset: {e}")
        import traceback
        traceback.print_exc()
        return
    
    if len(dataset) == 0:
        print("❌ Error: No samples loaded from dataset!")
        return
    
    # Split into train/val
    train_size = int(TRAIN_SPLIT * len(dataset))
    val_size = len(dataset) - train_size
    
    train_dataset, val_dataset = random_split(
        dataset, 
        [train_size, val_size],
        generator=torch.Generator().manual_seed(42)  # Reproducibility
    )
    
    print(f"Train samples: {len(train_dataset)}")
    print(f"Val samples: {len(val_dataset)}")
    
    # Analyze per-movement distribution
    analyze_dataset_distribution(dataset, train_dataset.indices, val_dataset.indices)
    print()
    
    # Create dataloaders
    train_loader = DataLoader(
        train_dataset, 
        batch_size=BATCH_SIZE, 
        shuffle=True,
        num_workers=0  # Use 0 for Windows compatibility
    )
    
    val_loader = DataLoader(
        val_dataset, 
        batch_size=BATCH_SIZE, 
        shuffle=False,
        num_workers=0
    )
    
    # Create model
    input_size = dataset.sequences[0].shape[1]  # Number of features
    
    model = ShoulderLSTM(
        input_size=input_size,
        hidden_size=HIDDEN_SIZE,
        num_layers=NUM_LAYERS,
        dropout=DROPOUT
    ).to(DEVICE)
    
    print(f"Model created:")
    print(f"  Input size: {input_size}")
    print(f"  Hidden size: {HIDDEN_SIZE}")
    print(f"  Num layers: {NUM_LAYERS}")
    print(f"  Total parameters: {sum(p.numel() for p in model.parameters()):,}")
    print()
    
    # Loss and optimizer
    criterion = nn.BCEWithLogitsLoss()
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)
    
    # Initialize CSV log file
    with open(LOG_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'epoch', 'train_loss', 'train_acc', 'val_loss', 'val_acc',
            'n_train', 'n_val', 'train_correct', 'val_correct'
        ])
    
    print(f"CSV log initialized: {LOG_FILE}")
    
    # Training loop
    best_val_loss = float('inf')
    best_val_accuracy = 0.0
    
    print("Starting training...")
    print()
    
    # Progress bar for epochs
    for epoch in tqdm(range(NUM_EPOCHS), desc="Training Progress", unit="epoch"):
        # Train
        train_loss, train_acc, train_correct, n_train = train_epoch(
            model, train_loader, criterion, optimizer, DEVICE, epoch+1, NUM_EPOCHS
        )
        
        # Validate
        val_loss, val_acc, val_correct, n_val = validate(
            model, val_loader, criterion, DEVICE, epoch+1, NUM_EPOCHS
        )
        
        # Log to CSV
        with open(LOG_FILE, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                epoch + 1, train_loss, train_acc, val_loss, val_acc,
                n_train, n_val, train_correct, val_correct
            ])
        
        # Print progress (one line per epoch)
        print(f"Epoch {epoch+1:3d}/{NUM_EPOCHS} | "
              f"Train: Loss={train_loss:.4f} Acc={train_acc:.4f} ({train_correct}/{n_train}) | "
              f"Val: Loss={val_loss:.4f} Acc={val_acc:.4f} ({val_correct}/{n_val})")
        
        # Save best model
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_val_accuracy = val_acc
            
            save_checkpoint(
                model=model,
                dataset=dataset,
                epoch=epoch + 1,
                val_loss=val_loss,
                val_accuracy=val_acc,
                filepath=MODEL_SAVE_PATH
            )
            
            print(f"         ⭐ New best model saved! Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.4f}")
    
    # Training complete
    print("\n" + "="*60)
    print("Training Complete!")
    print("="*60)
    print(f"Best validation loss: {best_val_loss:.4f}")
    print(f"Best validation accuracy: {best_val_accuracy:.4f}")
    print(f"Model saved to: {MODEL_SAVE_PATH}")
    print(f"Training log saved to: {LOG_FILE}")
    print()
    print("Next steps:")
    print("  1. Review training log: {LOG_FILE}")
    print("  2. Test the model with: python -m ml.models.lstm_quality")
    print("  3. Start Flask API: python ml/api_server.py")
    print("  4. Integrate with web demo")


# ============================================================
# Entry Point
# ============================================================

if __name__ == '__main__':
    train()
