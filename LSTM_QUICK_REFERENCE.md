# 🚀 LSTM Quick Reference Card

## Training Commands

```powershell
# 1. Train LSTM model (first time only)
cd ml
python train_lstm.py

# 2. Test components
python -m data.ui_prmd_loader        # Test data loader
python -m models.lstm_quality         # Test model architecture
python -m personalization             # Test personalizer
```

## Running the System

```powershell
# Use your existing Phase 7 script - it works unchanged!
.\START_PHASE7.ps1
```

## Testing API

```powershell
# Check if LSTM is loaded
Invoke-RestMethod -Uri "http://localhost:5000/health" -Method Get

# Test quality prediction
$body = @{
    user_id = "test_user"
    angles = @(@(80), @(85), @(90), @(95), @(100), @(95), @(90), @(85), @(80))
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/predict_quality" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body
```

## File Locations

```
ml/
├── data/
│   └── ui_prmd_loader.py          ← Dataset loader
├── models/
│   ├── lstm_quality.py            ← LSTM architecture
│   └── shoulder_lstm_model.pt     ← Trained model (after training)
├── train_lstm.py                  ← Training script
├── personalization.py             ← Adaptive personalization
└── api_server.py                  ← Flask API (EXTENDED)

demo/
├── utils/
│   └── lstmClient.js              ← JavaScript API client
└── exercises/
    └── shoulderExercise.js        ← Shoulder exercise (EXTENDED)
```

## Key Functions

### Python

```python
# In api_server.py
@app.route('/predict_quality', methods=['POST'])
def predict_quality():
    # Predicts movement quality for shoulder reps
    pass

# In personalization.py
personalizer.update_and_get_target(user_id, rep_rom, quality_score)
# Returns personalized target ROM
```

### JavaScript

```javascript
// In lstmClient.js
import { predictQuality } from './utils/lstmClient.js';

const result = await predictQuality(userId, angleSequence);
// Returns: {quality_score, rep_rom, personalized_target_angle}
```

## Configuration

### Dataset Path
**File:** `ml/train_lstm.py` (line ~30)
```python
DATA_ROOT = r"C:\...\UI-PRMD\Segmented Movements\Kinect\Angles"
```

### Personalization Settings
**File:** `ml/api_server.py` (line ~60)
```python
personalizer = RehabPersonalizer(
    base_increment_deg=5.0,      # Initial challenge increase
    max_extra_deg=30.0,          # Max ROM increase
    ema_alpha=0.3                # Quality smoothing
)
```

### Feature Selection
**File:** `ml/data/ui_prmd_loader.py` (line ~27)
```python
ANGLE_COLUMN_INDICES = list(range(0, 6)) + list(range(15, 27))  # 18 features
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Model not found | Run `python ml/train_lstm.py` |
| Feature mismatch | Check `ANGLE_COLUMN_INDICES` in data loader |
| No predictions | Verify LSTM loaded: check `/health` endpoint |
| Sequence too short | Ensure capturing angles every frame |

## Expected Output

### Training
```
Loading UI-PRMD shoulder dataset...
Loaded 40 reps, skipped 5
  Correct reps: 30
  Incorrect reps: 10
...
Epoch [50/50] Val Loss: 0.3245, Val Acc: 0.8750
✅ Checkpoint saved to: models/shoulder_lstm_model.pt
```

### API Server Startup
```
✅ Loaded RL model: ./models/dqn/DQN_rehab_final.zip
✅ Loaded LSTM model: ./models/shoulder_lstm_model.pt
   - Input size: 18
   - Sequence length: 100
   - Global max ROM: 145.3°
🚀 RL + LSTM API Server Starting...
Listening on http://localhost:5000
```

### Browser Console (After Rep)
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 LSTM Quality Prediction Results
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Quality Score: 87.5%
Rep ROM: 112.3°
Target ROM: 118.0°
Feedback: ✅ Great job! Form is looking good!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## API Response Examples

### /health
```json
{
  "status": "ok",
  "rl_model_loaded": true,
  "form_classifier_loaded": false,
  "lstm_model_loaded": true
}
```

### /predict_quality
```json
{
  "quality_score": 0.873,
  "rep_rom": 112.34,
  "personalized_target_angle": 118.0,
  "user_id": "user_123"
}
```

## Dependencies (Already in requirements.txt)

- ✅ `torch>=1.10.0`
- ✅ `scipy>=1.7.0`
- ✅ `flask>=2.3.0`
- ✅ `flask-cors>=4.0.0`
- ✅ `numpy>=1.21.0`

## Documentation Files

- 📖 `LSTM_INTEGRATION_GUIDE.md` - Detailed usage guide
- 📋 `LSTM_SUMMARY.md` - Implementation summary
- 🎯 `LSTM_QUICK_REFERENCE.md` - This file

## Success Checklist

- [ ] UI-PRMD dataset downloaded and extracted
- [ ] Dataset path configured in `train_lstm.py`
- [ ] Training completed successfully
- [ ] Model file exists: `ml/models/shoulder_lstm_model.pt`
- [ ] Flask server shows "LSTM model loaded"
- [ ] `/health` returns `lstm_model_loaded: true`
- [ ] Browser console shows quality predictions
- [ ] Target angle updates after reps

---

**Need help?** See `LSTM_INTEGRATION_GUIDE.md` for detailed instructions.
