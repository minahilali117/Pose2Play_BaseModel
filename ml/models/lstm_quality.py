"""
LSTM-based Movement Quality Classifier for Shoulder Rehabilitation

Architecture:
  - Input: [batch, seq_len, features] time-series of joint angles
  - Bidirectional LSTM layers for temporal feature extraction
  - Fully connected layers for binary classification (correct vs incorrect)
  - Output: Single logit for BCEWithLogitsLoss
"""

import torch
import torch.nn as nn


class ShoulderLSTM(nn.Module):
    """
    Bidirectional LSTM for shoulder exercise quality prediction.
    
    Architecture:
      - 2 stacked BiLSTM layers (128 hidden units total → 64 per direction)
      - Dropout for regularization
      - FC layers: hidden_size*2 → 32 → 1
      - Uses final hidden state from both directions
    """
    
    def __init__(self, 
                 input_size: int, 
                 hidden_size: int = 64,
                 num_layers: int = 2,
                 dropout: float = 0.3):
        """
        Args:
          input_size: Number of features per timestep (F)
          hidden_size: Hidden size for each LSTM direction
          num_layers: Number of stacked LSTM layers
          dropout: Dropout probability between LSTM layers
        """
        super(ShoulderLSTM, self).__init__()
        
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        # Bidirectional LSTM
        # output will be [batch, seq_len, hidden_size * 2] because bidirectional=True
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            bidirectional=True,
            dropout=dropout if num_layers > 1 else 0
        )
        
        # Fully connected layers
        # Input: hidden_size * 2 (concatenated forward + backward)
        self.fc1 = nn.Linear(hidden_size * 2, 32)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(dropout)
        self.fc2 = nn.Linear(32, 1)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass.
        
        Args:
          x: [batch, seq_len, input_size] tensor of angle sequences
        
        Returns:
          logits: [batch] tensor of raw logits (before sigmoid)
        """
        # LSTM forward pass
        # lstm_out: [batch, seq_len, hidden_size * 2]
        # h_n: [num_layers * 2, batch, hidden_size] (2 directions)
        # c_n: [num_layers * 2, batch, hidden_size]
        lstm_out, (h_n, c_n) = self.lstm(x)
        
        # Use final hidden states from both directions
        # h_n[-2]: final forward hidden state
        # h_n[-1]: final backward hidden state
        forward_hidden = h_n[-2, :, :]   # [batch, hidden_size]
        backward_hidden = h_n[-1, :, :]  # [batch, hidden_size]
        
        # Concatenate forward and backward
        combined = torch.cat([forward_hidden, backward_hidden], dim=1)  # [batch, hidden_size*2]
        
        # Fully connected layers
        out = self.fc1(combined)      # [batch, 32]
        out = self.relu(out)
        out = self.dropout(out)
        out = self.fc2(out)           # [batch, 1]
        
        # Squeeze to [batch]
        logits = out.squeeze(1)
        
        return logits
    
    def predict_proba(self, x: torch.Tensor) -> torch.Tensor:
        """
        Predict probabilities (applies sigmoid to logits).
        
        Args:
          x: [batch, seq_len, input_size] tensor
        
        Returns:
          probs: [batch] tensor of probabilities in [0, 1]
        """
        with torch.no_grad():
            logits = self.forward(x)
            probs = torch.sigmoid(logits)
        return probs


# ============================================================
# Model Summary / Testing
# ============================================================

def count_parameters(model: nn.Module) -> int:
    """Count trainable parameters."""
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


if __name__ == '__main__':
    # Test model instantiation
    print("Testing ShoulderLSTM model...")
    
    # Example configuration (matches data loader)
    input_size = 18  # Number of angle features
    seq_len = 100    # Sequence length
    batch_size = 16
    
    # Create model
    model = ShoulderLSTM(
        input_size=input_size,
        hidden_size=64,
        num_layers=2,
        dropout=0.3
    )
    
    print(f"\n✅ Model created successfully!")
    print(f"Total trainable parameters: {count_parameters(model):,}")
    
    # Test forward pass
    dummy_input = torch.randn(batch_size, seq_len, input_size)
    
    try:
        logits = model(dummy_input)
        print(f"\nForward pass successful!")
        print(f"  Input shape: {dummy_input.shape}")
        print(f"  Output shape: {logits.shape}")
        print(f"  Output range: [{logits.min().item():.3f}, {logits.max().item():.3f}]")
        
        # Test predict_proba
        probs = model.predict_proba(dummy_input)
        print(f"\nPredict proba successful!")
        print(f"  Probability range: [{probs.min().item():.3f}, {probs.max().item():.3f}]")
        
    except Exception as e:
        print(f"❌ Error during forward pass: {e}")
        import traceback
        traceback.print_exc()
    
    # Print model architecture
    print("\nModel Architecture:")
    print(model)
