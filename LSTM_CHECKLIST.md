# ✅ LSTM Integration Checklist

## Phase 1: Setup (Today)

### Dataset Preparation
- [ ] Download UI-PRMD dataset from [source link]
- [ ] Extract to a local directory
- [ ] Note the path to: `Segmented Movements/Kinect/Angles/`
- [ ] Verify files exist for m07 and m10 movements
- [ ] Check for both correct and `_inc` (incorrect) files

### Code Configuration
- [ ] Open `ml/train_lstm.py`
- [ ] Update `DATA_ROOT` variable (line ~30) with your dataset path
- [ ] Save the file

### Environment Check
- [ ] Ensure virtual environment is activated
- [ ] Run: `pip install -r ml/requirements.txt`
- [ ] Verify torch and scipy are installed

---

## Phase 2: Training (30 minutes)

### Initial Training
- [ ] Open PowerShell in project root
- [ ] Run: `cd ml`
- [ ] Run: `python train_lstm.py`
- [ ] Wait for training to complete (~5-10 minutes)
- [ ] Verify checkpoint created: `ml/models/shoulder_lstm_model.pt`

### Verify Training Success
- [ ] Check final validation accuracy > 70%
- [ ] Review training logs for any errors
- [ ] Note the `global_max_rom` value (shown in logs)
- [ ] Confirm model file size is ~5-10 MB

### Test Components
- [ ] Run: `python -m data.ui_prmd_loader`
  - Expected: Shows dataset stats
- [ ] Run: `python -m models.lstm_quality`
  - Expected: Shows model architecture and test forward pass
- [ ] Run: `python -m personalization`
  - Expected: Simulates 20 reps with adaptive targets

---

## Phase 3: Integration Testing (15 minutes)

### Start Flask Server
- [ ] Return to project root: `cd ..`
- [ ] Run: `.\START_PHASE7.ps1`
- [ ] New PowerShell window should open with Flask server
- [ ] Check for message: "✅ Loaded LSTM model"

### Verify API Health
- [ ] Open new PowerShell terminal
- [ ] Run: `Invoke-RestMethod -Uri "http://localhost:5000/health" -Method Get`
- [ ] Confirm response shows: `"lstm_model_loaded": true`

### Test Prediction Endpoint
- [ ] Create test request (see LSTM_QUICK_REFERENCE.md)
- [ ] Send POST to `/predict_quality`
- [ ] Verify response contains `quality_score`, `rep_rom`, `personalized_target_angle`
- [ ] Check response time < 100ms

---

## Phase 4: Browser Demo (10 minutes)

### Open Web Demo
- [ ] Browser should auto-open with `demo/index.html`
- [ ] Allow camera access when prompted
- [ ] Verify video feed shows pose skeleton

### Test Shoulder Exercise
- [ ] Press F12 to open browser console
- [ ] Perform a shoulder lateral raise
- [ ] Complete at least 3 reps
- [ ] Check console for LSTM prediction logs after each rep

### Expected Console Output
- [ ] See formatted prediction results table
- [ ] Quality score displayed (0-100%)
- [ ] Rep ROM shown in degrees
- [ ] Target ROM updates between reps
- [ ] Quality feedback message appears

---

## Phase 5: Validation (1 hour)

### Data Quality Check
- [ ] Perform 10 reps with **good form**
  - Controlled speed
  - Full range of motion
  - Proper alignment
- [ ] Check quality scores are consistently > 0.7
- [ ] Verify target increases gradually

### Intentional Errors
- [ ] Perform 5 reps with **poor form**
  - Too fast
  - Incomplete ROM
  - Jerky movement
- [ ] Check quality scores drop below 0.5
- [ ] Verify target decreases or stays same

### Personalization Testing
- [ ] Start fresh session (refresh browser)
- [ ] Perform 5 baseline reps
- [ ] Check console for "Baseline ROM established" message
- [ ] Continue 10 more reps
- [ ] Verify target adapts based on performance

---

## Phase 6: Documentation (30 minutes)

### Take Screenshots
- [ ] Training output showing final accuracy
- [ ] Flask server console with "LSTM model loaded"
- [ ] Browser console with prediction results
- [ ] Web demo showing exercise in progress

### Record Metrics
- [ ] Training time: _________ minutes
- [ ] Final validation accuracy: _________%
- [ ] Average inference latency: _________ ms
- [ ] Number of UI-PRMD samples used: _________

### Create Demo Video (Optional)
- [ ] Screen record 2-minute demo
- [ ] Show training script running
- [ ] Show Flask server starting
- [ ] Show live predictions in browser
- [ ] Show quality scores updating

---

## Phase 7: FYP Report Integration (2-3 hours)

### Write Methodology Section
- [ ] Describe UI-PRMD dataset selection
- [ ] Explain LSTM architecture choice (BiLSTM, 2 layers, 64 units)
- [ ] Document preprocessing steps (resampling, normalization)
- [ ] Describe personalization algorithm (EMA, target adjustment)

### Create Results Tables
- [ ] Training accuracy by epoch
- [ ] Confusion matrix (correct vs incorrect classification)
- [ ] Inference latency measurements
- [ ] User study results (if conducted)

### Add Figures
- [ ] LSTM architecture diagram
- [ ] Training loss curve
- [ ] Sample angle sequence visualization
- [ ] Personalization target progression graph

### Discussion Points
- [ ] Why LSTM over static thresholds?
- [ ] Advantages of per-user adaptation
- [ ] Limitations (small dataset, single exercise)
- [ ] Future work (multi-exercise models, attention mechanisms)

---

## Troubleshooting Checklist

### Issue: Training fails with "Dataset not found"
- [ ] Verify `DATA_ROOT` path in `train_lstm.py`
- [ ] Check dataset structure matches expected format
- [ ] Ensure files are named `mXX_sYY_eZZ_angles.txt`

### Issue: Low training accuracy (<60%)
- [ ] Check dataset has both correct and incorrect samples
- [ ] Verify labels are assigned correctly (`_inc` = incorrect)
- [ ] Try increasing `NUM_EPOCHS` to 100
- [ ] Consider data augmentation (not yet implemented)

### Issue: "LSTM model not found" on server start
- [ ] Confirm `shoulder_lstm_model.pt` exists in `ml/models/`
- [ ] Check file is not corrupted (size > 1 MB)
- [ ] Re-run training if needed

### Issue: No predictions in browser console
- [ ] Verify Flask server is running (check terminal)
- [ ] Test `/health` endpoint manually
- [ ] Check browser Network tab for failed requests
- [ ] Look for CORS errors in console

### Issue: "Feature mismatch" error
- [ ] Check angle sequence dimensions in JavaScript
- [ ] Verify `currentRepAngleSequence.push([shoulderAngle])` format
- [ ] Consider retraining model with single feature (see guide)

---

## Success Metrics

### Minimum Viable Product
- [x] LSTM model trains without errors
- [x] Flask API loads model successfully
- [x] Browser demo sends predictions requests
- [x] Quality scores displayed in console
- [x] Personalization updates targets

### Enhanced Version (Optional)
- [ ] User study with 10+ participants
- [ ] Collected quality score vs. expert ratings
- [ ] Statistical analysis of personalization effectiveness
- [ ] UI visualization of quality scores
- [ ] Extended to hip/knee exercises

### Publication Ready (Advanced)
- [ ] Dataset expanded to 100+ reps
- [ ] Model accuracy > 85%
- [ ] Validated on held-out subjects
- [ ] Comparison with baseline methods
- [ ] User satisfaction survey results

---

## Timeline Estimate

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| Setup | 30 min | Dataset download |
| Training | 10 min | Setup complete |
| Integration | 15 min | Training complete |
| Demo Testing | 10 min | Server running |
| Validation | 1 hour | Demo working |
| Documentation | 30 min | All tests passed |
| **Total** | **~2.5 hours** | - |

---

## Final Verification

Before considering LSTM integration complete:

- [ ] All Phase 1-4 items checked
- [ ] At least 3 successful end-to-end tests
- [ ] Screenshots saved for report
- [ ] Code committed to version control
- [ ] Documentation files read through
- [ ] Team members can replicate results

---

## Next Steps After Completion

1. **Immediate:**
   - Share trained model with team (upload to cloud)
   - Write up results for FYP report
   - Prepare demo for supervisor meeting

2. **Short-term:**
   - Extend to other exercises (hip, knee)
   - Improve UI with quality visualizations
   - Conduct user study for evaluation

3. **Long-term:**
   - Integrate with VR system
   - Add Firebase data logging
   - Deploy to production environment
   - Explore transformer architectures

---

## Questions to Answer for FYP Defense

Prepare answers to these likely questions:

- [ ] Why LSTM over simple feedforward network?
  - Answer: Captures temporal dynamics of movement
  
- [ ] How much data was used for training?
  - Answer: X reps from UI-PRMD dataset
  
- [ ] What is the model's accuracy?
  - Answer: X% validation accuracy
  
- [ ] How does personalization work?
  - Answer: EMA of quality scores adjusts target ROM
  
- [ ] What are the limitations?
  - Answer: Small dataset, single exercise type, requires training
  
- [ ] How does it compare to rule-based?
  - Answer: More nuanced, captures movement quality beyond angles
  
- [ ] What would you improve with more time?
  - Answer: Larger dataset, attention mechanisms, multi-exercise model

---

**Good luck with your FYP! 🎓🚀**

*This integration represents a significant technical achievement combining:*
- *Deep learning (LSTM)*
- *Real-time inference*
- *Adaptive personalization*
- *Full-stack development*
- *Research-grade implementation*
