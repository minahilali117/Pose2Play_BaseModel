"""
Data Processor for Rehabilitation Exercise Dataset
Extracts features from inertial and optical data for RL training

Dataset structure:
- inertial/lower/A/Lshin/A01HAAL0_1.csv (incorrect hip abduction)
- inertial/lower/A/Lshin/A01HAAL1_1.csv (correct hip abduction)
"""

import os
import pandas as pd
import numpy as np
from pathlib import Path
import json
from typing import Dict, List, Tuple
import re

class RehabDataProcessor:
    """Process rehabilitation exercise dataset for ML training"""
    
    # Exercise code mapping
    EXERCISE_MAPPING = {
        'GAT': 'gait',
        'GHT': 'gait_turning',
        'GIS': 'gait_stairs',
        'HAAL': 'hip_abduction_left',
        'HAAR': 'hip_adduction_right',
        'KFEL': 'knee_flexion_left',
        'KFER': 'knee_flexion_right',
        'SQT': 'squat'
    }
    
    # Sensor positions
    SENSOR_POSITIONS = ['Lshin', 'Lthigh', 'Rshin', 'Rthigh', 'Larm', 'Lforearm', 'Rarm', 'Rforearm']
    
    def __init__(self, dataset_path: str, output_path: str):
        self.dataset_path = Path(dataset_path)
        self.output_path = Path(output_path)
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        self.data_records = []
        
    def parse_filename(self, filename: str) -> Dict:
        """
        Parse filename to extract metadata
        Example: A01HAAL0_1.csv
        Returns: {subject: 'A', trial: '01', exercise: 'hip_abduction_left', 
                  correct: False, repetition: 1}
        """
        pattern = r'([A-E])(\d{2})([A-Z]+)([01])_(\d+)\.csv'
        match = re.match(pattern, filename)
        
        if not match:
            return None
            
        subject, trial, exercise_code, correct_label, rep = match.groups()
        
        return {
            'subject': subject,
            'trial': int(trial),
            'exercise_code': exercise_code,
            'exercise': self.EXERCISE_MAPPING.get(exercise_code, 'unknown'),
            'correct': correct_label == '1',
            'repetition': int(rep),
            'filename': filename
        }
    
    def load_inertial_data(self, filepath: Path) -> pd.DataFrame:
        """Load and clean inertial sensor data"""
        try:
            df = pd.DataFrame(pd.read_csv(filepath))
            
            # Rename columns for consistency
            df.columns = [
                'time', 'gyro_x', 'gyro_y', 'gyro_z',
                'accel_x', 'accel_y', 'accel_z',
                'mag_x', 'mag_y', 'mag_z'
            ]
            
            return df
        except Exception as e:
            print(f"Error loading {filepath}: {e}")
            return None
    
    def extract_features(self, df: pd.DataFrame) -> Dict:
        """Extract temporal and statistical features from sensor data"""
        if df is None or len(df) == 0:
            return None
            
        features = {}
        
        # Time-domain features for each sensor axis
        for axis in ['gyro_x', 'gyro_y', 'gyro_z', 'accel_x', 'accel_y', 'accel_z']:
            data = df[axis].values
            
            features[f'{axis}_mean'] = np.mean(data)
            features[f'{axis}_std'] = np.std(data)
            features[f'{axis}_min'] = np.min(data)
            features[f'{axis}_max'] = np.max(data)
            features[f'{axis}_range'] = np.max(data) - np.min(data)
            features[f'{axis}_median'] = np.median(data)
            
            # Peak features
            features[f'{axis}_peaks'] = len(self._find_peaks(data))
            
            # Zero crossing rate (for oscillatory movements)
            features[f'{axis}_zcr'] = self._zero_crossing_rate(data)
        
        # Movement quality metrics
        features['duration'] = df['time'].iloc[-1] - df['time'].iloc[0]
        features['smoothness'] = self._calculate_smoothness(df)
        features['symmetry'] = self._calculate_symmetry(df)
        
        return features
    
    def _find_peaks(self, data: np.ndarray, threshold=0.5) -> np.ndarray:
        """Simple peak detection"""
        mean = np.mean(data)
        std = np.std(data)
        peaks = []
        
        for i in range(1, len(data) - 1):
            if data[i] > data[i-1] and data[i] > data[i+1]:
                if abs(data[i] - mean) > threshold * std:
                    peaks.append(i)
        
        return np.array(peaks)
    
    def _zero_crossing_rate(self, data: np.ndarray) -> float:
        """Calculate zero crossing rate (frequency of oscillation)"""
        crossings = np.where(np.diff(np.signbit(data)))[0]
        return len(crossings) / len(data)
    
    def _calculate_smoothness(self, df: pd.DataFrame) -> float:
        """Calculate movement smoothness (lower jerk = smoother)"""
        # Jerk = derivative of acceleration
        jerk_x = np.diff(df['accel_x'].values)
        jerk_y = np.diff(df['accel_y'].values)
        jerk_z = np.diff(df['accel_z'].values)
        
        # Total jerk magnitude
        total_jerk = np.sqrt(jerk_x**2 + jerk_y**2 + jerk_z**2)
        
        # Smoothness = negative log of jerk (higher = smoother)
        smoothness = -np.log(np.mean(total_jerk) + 1e-6)
        
        return smoothness
    
    def _calculate_symmetry(self, df: pd.DataFrame) -> float:
        """Calculate left-right symmetry (placeholder - needs paired sensors)"""
        # This would require comparing left vs right sensor data
        # For now, return a default value
        return 1.0
    
    def process_sensor_data(self, sensor_dir: Path, subject: str, body_part: str) -> List[Dict]:
        """Process all CSV files in a sensor directory"""
        records = []
        
        if not sensor_dir.exists():
            return records
        
        for csv_file in sensor_dir.glob('*.csv'):
            # Skip calibration files
            if 'Calib' in csv_file.name:
                continue
                
            metadata = self.parse_filename(csv_file.name)
            if not metadata:
                continue
            
            # Load sensor data
            df = self.load_inertial_data(csv_file)
            if df is None:
                continue
            
            # Extract features
            features = self.extract_features(df)
            if not features:
                continue
            
            # Combine metadata + features
            record = {
                **metadata,
                'sensor_position': body_part,
                **features
            }
            
            records.append(record)
        
        return records
    
    def process_dataset(self, focus_exercises: List[str] = None):
        """
        Process entire dataset
        
        Args:
            focus_exercises: Filter by specific exercises (e.g., ['hip_abduction_left', 'squat'])
        """
        print("🔄 Processing rehabilitation dataset...")
        
        # Process inertial data (lower body - hips & knees)
        inertial_lower = self.dataset_path / 'inertial' / 'lower'
        
        for subject_dir in inertial_lower.glob('*'):
            if not subject_dir.is_dir():
                continue
                
            subject = subject_dir.name
            print(f"\n📊 Processing subject {subject}...")
            
            for sensor_pos in self.SENSOR_POSITIONS[:4]:  # Lower body sensors
                sensor_dir = subject_dir / sensor_pos
                
                if not sensor_dir.exists():
                    continue
                
                records = self.process_sensor_data(sensor_dir, subject, sensor_pos)
                
                # Filter by focus exercises if specified
                if focus_exercises:
                    records = [r for r in records if r['exercise'] in focus_exercises]
                
                self.data_records.extend(records)
                
                print(f"  ✓ {sensor_pos}: {len(records)} recordings")
        
        print(f"\n✅ Total recordings processed: {len(self.data_records)}")
        
        # Save to CSV
        self._save_processed_data()
        
        # Generate statistics
        self._generate_statistics()
        
        return self.data_records
    
    def _save_processed_data(self):
        """Save processed data to CSV"""
        if not self.data_records:
            print("⚠️  No data to save")
            return
        
        df = pd.DataFrame(self.data_records)
        
        output_file = self.output_path / 'processed_features.csv'
        df.to_csv(output_file, index=False)
        
        print(f"\n💾 Saved processed data to: {output_file}")
        print(f"   Shape: {df.shape}")
        print(f"   Columns: {len(df.columns)}")
    
    def _generate_statistics(self):
        """Generate dataset statistics"""
        if not self.data_records:
            return
        
        df = pd.DataFrame(self.data_records)
        
        stats = {
            'total_recordings': len(df),
            'subjects': df['subject'].nunique(),
            'exercises': df['exercise'].value_counts().to_dict(),
            'correct_distribution': df['correct'].value_counts().to_dict(),
            'sensor_positions': df['sensor_position'].value_counts().to_dict(),
            'feature_count': len([c for c in df.columns if '_mean' in c or '_std' in c])
        }
        
        # Save statistics
        stats_file = self.output_path / 'dataset_statistics.json'
        with open(stats_file, 'w') as f:
            json.dump(stats, indent=2, fp=f)
        
        print(f"\n📈 Dataset Statistics:")
        print(f"   Total recordings: {stats['total_recordings']}")
        print(f"   Unique subjects: {stats['subjects']}")
        print(f"   Exercises: {stats['exercises']}")
        print(f"   Correct/Incorrect: {stats['correct_distribution']}")
        print(f"   Features extracted: {stats['feature_count']}")
        
        print(f"\n💾 Saved statistics to: {stats_file}")
    
    def create_train_test_split(self, test_size=0.2, val_size=0.1):
        """Create train/val/test splits (stratified by subject)"""
        if not self.data_records:
            print("⚠️  No data available for splitting")
            return
        
        df = pd.DataFrame(self.data_records)
        
        # Get unique subjects
        subjects = df['subject'].unique()
        np.random.shuffle(subjects)
        
        # Split subjects
        n_test = int(len(subjects) * test_size)
        n_val = int(len(subjects) * val_size)
        
        test_subjects = subjects[:n_test]
        val_subjects = subjects[n_test:n_test+n_val]
        train_subjects = subjects[n_test+n_val:]
        
        # Create splits
        train_df = df[df['subject'].isin(train_subjects)]
        val_df = df[df['subject'].isin(val_subjects)]
        test_df = df[df['subject'].isin(test_subjects)]
        
        # Save splits
        train_df.to_csv(self.output_path / 'train.csv', index=False)
        val_df.to_csv(self.output_path / 'val.csv', index=False)
        test_df.to_csv(self.output_path / 'test.csv', index=False)
        
        print(f"\n✂️  Data Split:")
        print(f"   Train: {len(train_df)} ({len(train_subjects)} subjects)")
        print(f"   Val: {len(val_df)} ({len(val_subjects)} subjects)")
        print(f"   Test: {len(test_df)} ({len(test_subjects)} subjects)")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Process rehabilitation exercise dataset')
    parser.add_argument('--input', type=str, default='../Dataset',
                        help='Path to dataset directory')
    parser.add_argument('--output', type=str, default='./data/processed',
                        help='Output directory for processed data')
    parser.add_argument('--exercises', nargs='+', default=None,
                        help='Focus on specific exercises (e.g., squat hip_abduction_left)')
    
    args = parser.parse_args()
    
    # Process dataset
    processor = RehabDataProcessor(args.input, args.output)
    processor.process_dataset(focus_exercises=args.exercises)
    processor.create_train_test_split()
    
    print("\n✅ Data processing complete!")
    print(f"📁 Processed data saved to: {args.output}")
