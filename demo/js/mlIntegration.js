// ML Integration Module - LSTM and RL
export class MLIntegration {
    constructor() {
        this.lstmEnabled = true;
        this.lastFormCheck = 0;
        this.userId = 'user_' + Date.now();
        this.sessionStartTime = null;
        this.lstmAdjustmentCount = 0;
        this.rlAdjustmentCount = 0;
    }
    
    setSessionStartTime(timestamp) {
        this.sessionStartTime = timestamp;
    }

    // LSTM Quality Prediction (Micro-adjustments ±2°)
    async predictLSTMQuality(angleSequence, repData) {
        try {
            const response = await fetch('/predict_quality', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: this.userId,
                    angles: angleSequence
                })
            });
            
            if (!response.ok) {
                console.error('LSTM API error:', response.status);
                return null;
            }
            
            const result = await response.json();
            
            // Log results
            console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
            console.log('🤖 LSTM Quality Analysis');
            console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
            console.log(`Quality Score: ${(result.quality_score * 100).toFixed(1)}%`);
            console.log(`Rep ROM: ${result.rep_rom.toFixed(1)}°`);
            console.log(`Target ROM: ${result.personalized_target_angle.toFixed(1)}°`);
            console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
            
            // COOPERATIVE ADJUSTMENT: LSTM makes micro-adjustments (±2°)
            const currentTarget = repData.targetAngle;
            let newTarget = currentTarget;
            
            if (result.personalized_target_angle) {
                const lstmSuggestion = Math.round(result.personalized_target_angle);
                const adjustment = lstmSuggestion - currentTarget;
                
                if (Math.abs(adjustment) <= 2) {
                    console.log(`🧠 LSTM micro-adjustment: ${currentTarget}° → ${lstmSuggestion}° (quality: ${(result.quality_score * 100).toFixed(0)}%)`);
                    newTarget = lstmSuggestion;
                    this.lstmAdjustmentCount++;
                } else {
                    console.log(`🧠 LSTM suggests ${lstmSuggestion}° (deferred to RL for large changes)`);
                }
            }
            
            return { 
                newTarget, 
                quality_score: result.quality_score,
                rep_rom: result.rep_rom,
                personalized_target_angle: result.personalized_target_angle
            };
        } catch (error) {
            console.error('LSTM prediction failed:', error);
            return null;
        }
    }

    // RL Adjustment (Macro-adjustments ±5° every 5 reps)
    async applyRLAdjustment(repCount, userHistory, currentTarget) {
        if (repCount % 5 !== 0) return { newTarget: currentTarget };
        
        // Pad userHistory to have at least 10 entries
        const paddedHistory = [...userHistory];
        while (paddedHistory.length < 10) {
            paddedHistory.unshift({ angle: currentTarget, quality: 'neutral' });
        }
        
        // Build state from user history (20 dimensions)
        const last10Angles = paddedHistory.slice(-10).map(r => r.angle || currentTarget);
        const consistency = this.getConsistency(paddedHistory);
        const fatigue = this.getFatigue(paddedHistory);
        const sessionTimeNorm = this.sessionStartTime ? Math.min((Date.now() - this.sessionStartTime) / 60000, 1) : 0;
        const baseline = paddedHistory[0]?.angle || currentTarget;
        const repsNorm = Math.min(repCount, 99) / 100;
        const successRate = this.getSuccessRate(paddedHistory);
        
        const state = [
            ...last10Angles,
            consistency,
            fatigue,
            sessionTimeNorm,
            currentTarget,
            baseline,
            repsNorm,
            successRate,
            0, 0, 0
        ];
        
        try {
            const response = await fetch('/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ state })
            });
            
            if (!response.ok) {
                console.error('RL API error:', response.status);
                return { 
                    newTarget: currentTarget,
                    consistency,
                    fatigue,
                    successRate,
                    actionName: 'API Error',
                    action: -1
                };
            }
            
            const result = await response.json();
            const action = result.action;
            
            let newTarget = currentTarget;
            let actionName = '';
            
            switch(action) {
                case 0:
                    newTarget = currentTarget + 5;
                    actionName = 'Decrease difficulty';
                    break;
                case 1:
                    actionName = 'Maintain level';
                    break;
                case 2:
                    newTarget = currentTarget - 5;
                    actionName = 'Increase difficulty';
                    break;
                case 3:
                    actionName = 'Rest recommended';
                    break;
                case 4:
                    actionName = 'Encouragement';
                    break;
            }
            
            if (newTarget !== currentTarget) {
                this.rlAdjustmentCount++;
            }
            
            console.log(`🎯 RL Action: ${actionName} | Target: ${currentTarget}° → ${newTarget}°`);
            
            return {
                newTarget,
                consistency,
                fatigue,
                successRate,
                actionName,
                action
            };
        } catch (error) {
            console.error('RL adjustment failed:', error);
            return { 
                newTarget: currentTarget,
                consistency,
                fatigue,
                successRate,
                actionName: 'Error',
                action: -1
            };
        }
    }

    // Form Analysis
    async analyzeForm(currentAngle, currentExercise, sessionReps) {
        const now = Date.now();
        if (now - this.lastFormCheck < 2000) return;
        this.lastFormCheck = now;

        try {
            const angles = {};
            if (currentExercise === 'squat') {
                angles.knee_left = currentAngle;
                angles.knee_right = currentAngle;
            } else if (currentExercise === 'hip') {
                angles.hip_left = currentAngle;
            } else if (currentExercise === 'shoulder') {
                angles.shoulder_left = currentAngle;
            }

            const movementSpeed = sessionReps.length > 1 
                ? (sessionReps[sessionReps.length - 1].timestamp - sessionReps[sessionReps.length - 2].timestamp) / 1000
                : 3.0;

            const response = await fetch('/predict_form_simple', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    angles: angles,
                    movement_speed: movementSpeed,
                    exercise_type: currentExercise === 'hip' ? 'hip_abduction_left' : currentExercise
                })
            });

            if (!response.ok) {
                console.log('[Form API] Not available (using offline mode)');
                return null;
            }

            const result = await response.json();
            console.log('[Form Analysis]', result);
            return result;
        } catch (error) {
            console.log('[Form API] Error:', error.message);
            return null;
        }
    }

    // Helper functions
    getConsistency(history) {
        if (history.length < 3) return 0.5;
        const angles = history.slice(-5).map(r => r.angle || 0);
        const avg = angles.reduce((a, b) => a + b, 0) / angles.length;
        const variance = angles.reduce((sum, angle) => sum + Math.pow(angle - avg, 2), 0) / angles.length;
        const stdDev = Math.sqrt(variance);
        return Math.max(0, Math.min(1, 1 - (stdDev / 30)));
    }

    getFatigue(history) {
        if (history.length < 5) return 0;
        const halfPoint = Math.floor(history.length / 2);
        const recentHalf = history.slice(halfPoint).map(r => r.angle || 0);
        const earlierHalf = history.slice(0, halfPoint).map(r => r.angle || 0);
        const recentAvg = recentHalf.reduce((a, b) => a + b, 0) / recentHalf.length;
        const earlierAvg = earlierHalf.reduce((a, b) => a + b, 0) / earlierHalf.length;
        const deterioration = Math.abs(earlierAvg - recentAvg) / Math.max(earlierAvg, recentAvg, 1);
        return Math.max(0, Math.min(1, deterioration));
    }

    getSuccessRate(history) {
        if (history.length === 0) return 0.5;
        const successful = history.filter(r => r.quality === 'good' || r.quality === 'perfect').length;
        return successful / history.length;
    }
    
    // Reset ML counters
    reset() {
        this.lstmAdjustmentCount = 0;
        this.rlAdjustmentCount = 0;
    }
}
