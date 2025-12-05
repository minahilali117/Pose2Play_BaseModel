"""
UI-PRMD Dataset Loader for Shoulder Rehabilitation LSTM Training

Loads segmented shoulder exercise repetitions from the UI-PRMD dataset.
Focuses on:
  - m07: Standing shoulder abduction
  - m10: Standing shoulder scaption

Each segmented file represents ONE repetition.
Labels:
  - 1 (correct): Files from 'Segmented Movements/Kinect/Angles/'
  - 0 (incorrect): Files from 'Incorrect Segmented Movements/Kinect/Angles/'

Folder location is the source of truth for labels, not filename suffix.
"""

import os
import numpy as np
import torch
from torch.utils.data import Dataset
from pathlib import Path
from scipy.interpolate import interp1d
from typing import List, Tuple, Dict
import re
from tqdm import tqdm


# ============================================================
# CONFIGURATION: Adjust these for your dataset structure
# ============================================================

# Target movements for shoulder exercises
TARGET_MOVEMENTS = ['m07', 'm10']  # m07=abduction, m10=scaption

# Sequence length for LSTM (all reps resampled to this length)
SEQ_LEN = 100

# Joint angle column indices from UI-PRMD Kinect data
# Based on UI-PRMD paper, Kinect provides 20 joints with 3 angle components each
# For shoulder exercises, we focus on:
#   - Shoulder joints (left/right): columns 15-20
#   - Spine/trunk stabilization: columns 0-5
#   - Elbow (for arm alignment): columns 21-26
ANGLE_COLUMN_INDICES = list(range(0, 6)) + list(range(15, 27))  # 18 features total

# Robust path resolution (works regardless of where repo is located)
ML_DIR = Path(__file__).resolve().parents[1]  # ml/ directory
DATA_ROOT = ML_DIR / "data" / "UI-PRMD"

# Separate directories for correct and incorrect reps
CORRECT_SEG_ROOT = DATA_ROOT / "Segmented Movements" / "Kinect" / "Angles"
INCORRECT_SEG_ROOT = DATA_ROOT / "Incorrect Segmented Movements" / "Kinect" / "Angles"

# Alternative: If your dataset has column names, uncomment and adjust:
# ANGLE_COLUMN_NAMES = [
#     'SpineBase_x', 'SpineBase_y', 'SpineBase_z',
#     'SpineMid_x', 'SpineMid_y', 'SpineMid_z',
#     'ShoulderLeft_x', 'ShoulderLeft_y', 'ShoulderLeft_z',
#     'ShoulderRight_x', 'ShoulderRight_y', 'ShoulderRight_z',
#     'ElbowLeft_x', 'ElbowLeft_y', 'ElbowLeft_z',
#     'ElbowRight_x', 'ElbowRight_y', 'ElbowRight_z'
# ]


def parse_filename(filename: str) -> Dict[str, any]:
    """
    Parse UI-PRMD filename to extract metadata.
    
    Examples:
      - m07_s03_e05_angles.txt → {movement: 7, subject: 3, episode: 5, incorrect: False}
      - m10_s12_e08_angles_inc.txt → {movement: 10, subject: 12, episode: 8, incorrect: True}
    
    Returns:
      dict with keys: movement, subject, episode, incorrect, or None if pattern doesn't match
    """
    # Pattern: mXX_sYY_eZZ_angles[_inc].txt
    # The _inc suffix is optional and indicates incorrect form
    pattern = r'm(\d+)_s(\d+)_e(\d+)_angles(_inc)?\.txt'
    match = re.match(pattern, filename)
    
    if not match:
        return None
    
    is_incorrect = match.group(4) is not None  # True if '_inc' suffix present
    
    return {
        'movement': int(match.group(1)),
        'subject': int(match.group(2)),
        'episode': int(match.group(3)),
        'incorrect': is_incorrect
    }


def load_angle_file(filepath: str, column_indices: List[int]) -> np.ndarray:
    """
    Load a single UI-PRMD angle file.
    
    Args:
      filepath: Path to .txt file
      column_indices: Which columns to extract
    
    Returns:
      np.ndarray of shape [T_raw, F] where:
        T_raw = number of timesteps in original file
        F = len(column_indices)
    """
    try:
        # Load CSV with comma delimiter
        data = np.loadtxt(filepath, delimiter=',')
        
        # Handle single-row files (expand dims)
        if data.ndim == 1:
            data = data.reshape(1, -1)
        
        # Select relevant columns
        if data.shape[1] > max(column_indices):
            selected = data[:, column_indices]
        else:
            # If file has fewer columns than expected, pad with zeros
            selected = np.zeros((data.shape[0], len(column_indices)))
            available_cols = min(data.shape[1], max(column_indices) + 1)
            selected[:, :available_cols] = data[:, :available_cols]
        
        return selected
    
    except Exception as e:
        print(f"Warning: Failed to load {filepath}: {e}")
        return None


def resample_sequence(sequence: np.ndarray, target_length: int) -> np.ndarray:
    """
    Resample a time-series sequence to a fixed length using linear interpolation.
    
    Args:
      sequence: [T_raw, F] array
      target_length: Desired sequence length
    
    Returns:
      [target_length, F] array
    """
    T_raw, F = sequence.shape
    
    if T_raw == target_length:
        return sequence
    
    # Create interpolation function for each feature
    original_indices = np.linspace(0, T_raw - 1, T_raw)
    target_indices = np.linspace(0, T_raw - 1, target_length)
    
    resampled = np.zeros((target_length, F))
    
    for f in range(F):
        interpolator = interp1d(original_indices, sequence[:, f], kind='linear')
        resampled[:, f] = interpolator(target_indices)
    
    return resampled


def compute_rep_rom(sequence: np.ndarray) -> float:
    """
    Compute range of motion (ROM) for a repetition.
    
    ROM = max(|angles|) across all timesteps and features.
    
    Args:
      sequence: [T, F] array of joint angles
    
    Returns:
      ROM in degrees
    """
    return float(np.max(np.abs(sequence)))


class ShoulderRehabDataset(Dataset):
    """
    PyTorch dataset for shoulder rehabilitation movement quality classification.
    
    Loads UI-PRMD segmented shoulder exercises (m07, m10) and prepares them for LSTM training.
    
    Features:
      - Automatic resampling to fixed sequence length
      - Global feature-wise normalization (z-score)
      - ROM computation for each repetition
      - Train/val split support
      - Loads both correct and incorrect (_inc) reps
    """
    
    def __init__(self, 
                 data_root: str = None,
                 movements: List[str] = TARGET_MOVEMENTS,
                 seq_len: int = SEQ_LEN,
                 column_indices: List[int] = ANGLE_COLUMN_INDICES,
                 normalize: bool = True):
        """
        Args:
          data_root: Path to UI-PRMD base directory (contains 'Segmented Movements' and 'Incorrect Segmented Movements')
                    If None, uses automatic path resolution from __file__
          movements: List of movement codes (e.g., ['m07', 'm10'])
          seq_len: Target sequence length for LSTM
          column_indices: Which angle columns to use
          normalize: Whether to apply z-score normalization
        """
        # Set paths for correct and incorrect reps
        if data_root is None:
            self.correct_root = CORRECT_SEG_ROOT
            self.incorrect_root = INCORRECT_SEG_ROOT
        else:
            base = Path(data_root)
            self.correct_root = base / "Segmented Movements" / "Kinect" / "Angles"
            self.incorrect_root = base / "Incorrect Segmented Movements" / "Kinect" / "Angles"
        
        self.movements = movements
        self.seq_len = seq_len
        self.column_indices = column_indices
        self.normalize = normalize
        
        # Storage for loaded data
        self.sequences = []  # List of [seq_len, F] arrays
        self.labels = []     # List of binary labels (0 or 1)
        self.roms = []       # List of ROM values
        self.metadata = []   # List of dicts with filename info
        
        # Statistics for normalization
        self.angle_mean = None
        self.angle_std = None
        self.global_max_rom = 0.0
        
        # Load all data
        self._load_dataset()
        
        # Compute normalization statistics
        if self.normalize:
            self._compute_normalization()
    
    def _load_dataset(self):
        """Scan both correct and incorrect directories and load all matching files."""
        print(f"Loading UI-PRMD shoulder dataset...")
        print(f"  Correct reps from: {self.correct_root}")
        print(f"  Incorrect reps from: {self.incorrect_root}")
        
        # Check if directories exist
        if not self.correct_root.exists():
            raise FileNotFoundError(f"Correct reps path not found: {self.correct_root}")
        if not self.incorrect_root.exists():
            raise FileNotFoundError(f"Incorrect reps path not found: {self.incorrect_root}")
        
        # Find all angle files from both directories
        correct_files = sorted(self.correct_root.glob('*.txt'))
        incorrect_files = sorted(self.incorrect_root.glob('*.txt'))
        
        print(f"\nFound {len(correct_files)} files in correct directory")
        print(f"Found {len(incorrect_files)} files in incorrect directory")
        print(f"Filtering for movements: {self.movements}")
        
        # Create combined list with (filepath, label) tuples
        # Label is based on directory, NOT filename suffix
        all_files = [(p, 1) for p in correct_files] + [(p, 0) for p in incorrect_files]
        
        loaded_count = 0
        skipped_count = 0
        num_correct = 0
        num_incorrect = 0
        
        # Use tqdm for progress bar
        for filepath, label in tqdm(all_files, desc="Loading UI-PRMD reps", unit="file"):
            filename = filepath.name
            
            # Parse filename to get movement code
            metadata = parse_filename(filename)
            
            if metadata is None:
                skipped_count += 1
                continue
            
            # Filter by target movements (m07, m10)
            movement_code = f"m{metadata['movement']:02d}"
            if movement_code not in self.movements:
                skipped_count += 1
                continue
            
            # Load angle data
            sequence = load_angle_file(str(filepath), self.column_indices)
            
            if sequence is None or len(sequence) < 3:
                # Skip files with too few frames
                skipped_count += 1
                continue
            
            # Resample to fixed length
            resampled = resample_sequence(sequence, self.seq_len)
            
            # Compute ROM
            rep_rom = compute_rep_rom(resampled)
            
            # Store (label already determined by directory)
            self.sequences.append(resampled)
            self.labels.append(label)
            self.roms.append(rep_rom)
            self.metadata.append({**metadata, 'filename': filename, 'label': label})
            
            loaded_count += 1
            
            # Track counts
            if label == 1:
                num_correct += 1
            else:
                num_incorrect += 1
        
        print(f"\n{'='*60}")
        print(f"Dataset Loading Summary:")
        print(f"  Total files scanned: {len(all_files)}")
        print(f"  Loaded reps: {loaded_count}")
        print(f"  Skipped files: {skipped_count}")
        print(f"  Correct reps (label=1): {num_correct}")
        print(f"  Incorrect reps (label=0): {num_incorrect}")
        print(f"{'='*60}")
        
        if loaded_count == 0:
            raise ValueError("No valid repetitions found! Check dataset paths and movement codes.")
        
        if num_incorrect == 0:
            print("\n⚠️  WARNING: No incorrect reps found!")
            print(f"   - Check if files exist in: {self.incorrect_root}")
            print(f"   - Looking for movements: {self.movements}")
        
        if num_correct == 0:
            print("\n⚠️  WARNING: No correct reps found!")
            print(f"   - Check if files exist in: {self.correct_root}")
            print(f"   - Looking for movements: {self.movements}")
    
    def _compute_normalization(self):
        """Compute global mean/std and normalize all sequences in-place."""
        # Stack all sequences
        all_sequences = np.stack(self.sequences, axis=0)  # [N, seq_len, F]
        
        # Compute feature-wise mean and std
        self.angle_mean = np.mean(all_sequences, axis=(0, 1))  # [F]
        self.angle_std = np.std(all_sequences, axis=(0, 1)) + 1e-6  # [F], avoid div by zero
        
        # Compute global max ROM
        self.global_max_rom = float(np.max(self.roms))
        
        # Normalize in-place
        for i in range(len(self.sequences)):
            self.sequences[i] = (self.sequences[i] - self.angle_mean) / self.angle_std
        
        print(f"Normalization stats computed:")
        print(f"  Mean range: [{self.angle_mean.min():.2f}, {self.angle_mean.max():.2f}]")
        print(f"  Std range: [{self.angle_std.min():.2f}, {self.angle_std.max():.2f}]")
        print(f"  Global max ROM: {self.global_max_rom:.2f}°")
    
    def __len__(self) -> int:
        return len(self.sequences)
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Returns:
          sequence: [seq_len, F] tensor
          label: scalar tensor (0 or 1)
          rom: scalar tensor (ROM in degrees)
        """
        sequence = torch.FloatTensor(self.sequences[idx])
        label = torch.FloatTensor([self.labels[idx]])
        rom = torch.FloatTensor([self.roms[idx]])
        
        return sequence, label, rom
    
    def get_normalization_params(self) -> Dict[str, np.ndarray]:
        """Returns normalization parameters for saving to checkpoint."""
        return {
            'angle_mean': self.angle_mean,
            'angle_std': self.angle_std,
            'global_max_rom': self.global_max_rom
        }


# ============================================================
# Testing / Quick Verification
# ============================================================

if __name__ == '__main__':
    # Test the data loader
    import sys
    
    # Use automatic path resolution (no hardcoded paths needed!)
    print(f"UI-PRMD base directory: {DATA_ROOT}")
    print(f"Correct reps: {CORRECT_SEG_ROOT}")
    print(f"Incorrect reps: {INCORRECT_SEG_ROOT}")
    
    if not DATA_ROOT.exists():
        print(f"\nDataset not found at: {DATA_ROOT}")
        print("Please ensure UI-PRMD dataset is extracted to ml/data/UI-PRMD/")
        sys.exit(1)
    
    if not CORRECT_SEG_ROOT.exists() or not INCORRECT_SEG_ROOT.exists():
        print(f"\nRequired subdirectories not found!")
        print(f"  Correct: {CORRECT_SEG_ROOT.exists()}")
        print(f"  Incorrect: {INCORRECT_SEG_ROOT.exists()}")
        sys.exit(1)
    
    try:
        # Use default DATA_ROOT (no need to specify)
        dataset = ShoulderRehabDataset()
        
        print(f"\n✅ Dataset loaded successfully!")
        print(f"Total samples: {len(dataset)}")
        
        # Test a few samples
        for i in range(min(3, len(dataset))):
            seq, label, rom = dataset[i]
            print(f"\nSample {i}:")
            print(f"  Sequence shape: {seq.shape}")
            print(f"  Label: {'Correct' if label.item() > 0.5 else 'Incorrect'}")
            print(f"  ROM: {rom.item():.2f}°")
        
    except Exception as e:
        print(f"❌ Error loading dataset: {e}")
        import traceback
        traceback.print_exc()
