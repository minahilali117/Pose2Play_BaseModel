/**
 * Shoulder Exercise Example: Lateral Shoulder Raise (with Adaptive Learning & Rewards)
 * 
 * This demonstrates how to track shoulder angles for exercises like
 * lateral raises, shoulder abduction, or external rotation with personalized targets
 * and reward system integration.
 */

import { calculateAngle } from '../utils/angles.js';
import { visibilityCheck } from '../utils/visibility.js';
import { 
    trackRepPerformance, 
    trackSessionPerformance, 
    calculatePersonalTarget,
    getProgressionRecommendation 
} from '../utils/adaptiveLearning.js';
import { 
    processSessionRewards 
} from '../utils/rewardSystem.js';
import { 
    predictQuality, 
    checkLSTMAvailability,
    getQualityFeedback,
    logPrediction 
} from '../utils/lstmClient.js';

/**
 * Shoulder Exercise Configuration
 */
export const shoulderExerciseConfig = {
    name: "Lateral Shoulder Raise",
    
    states: {
        DOWN: { 
            feedback: "Raise your arms!", 
            audio: false, 
            countRep: false, 
            color: "yellow" 
        },
        RAISING: { 
            feedback: "Keep lifting!", 
            audio: false, 
            countRep: false, 
            color: "yellow" 
        },
        TARGET_REACHED: { 
            feedback: "Perfect height! Hold it.", 
            audio: true, 
            countRep: false, 
            color: "green" 
        },
        LOWERING: { 
            feedback: "Slowly lower!", 
            audio: false, 
            countRep: false, 
            color: "blue" 
        },
        COMPLETED: { 
            feedback: "Great rep!", 
            audio: true, 
            countRep: true, 
            color: "green" 
        }
    },

    transitions: {
        DOWN: {
            raising: "RAISING"
        },
        RAISING: {
            targetReached: "TARGET_REACHED",
            lowering: "DOWN"
        },
        TARGET_REACHED: {
            lowering: "LOWERING"
        },
        LOWERING: {
            completed: "COMPLETED"
        },
        COMPLETED: {
            raising: "RAISING"
        }
    },

    jointInfo: {
        landmarks: {
            leftShoulder: 11,
            leftElbow: 13,
            leftWrist: 15,
            leftHip: 23,
            rightShoulder: 12,
            rightElbow: 14,
            rightWrist: 16,
            rightHip: 24
        }
    },

    targets: {
        downAngle: 30,           // Arm at side
        targetShoulderAngle: 90,  // Arm raised to shoulder height (horizontal)
        raisingThreshold: 50      // Angle when starting to raise
    }
};

let currentState = "DOWN";
let repCount = 0;
let lastShoulderAngle = 30;
let sessionReps = [];
let repStartTime = null;
let repMinAngle = 0;
let repMaxAngle = 0;

// LSTM integration: Track angle sequence for current rep
let currentRepAngleSequence = [];
let lstmEnabled = false;
let personalizedTargetAngle = 90; // Updated by LSTM personalizer

// Check LSTM availability on module load
checkLSTMAvailability().then(available => {
    lstmEnabled = available;
    if (lstmEnabled) {
        console.log('✅ LSTM movement quality model available');
    } else {
        console.log('⚠️ LSTM model not available - using rule-based feedback only');
    }
});

/**
 * Check shoulder exercise form (with adaptive learning)
 * 
 * This tracks the angle between shoulder-elbow-hip to measure arm elevation.
 * 
 * @param {Array} landmarks - MediaPipe pose landmarks
 * @param {Function} onFeedbackUpdate - Callback for feedback
 * @param {Function} setCurrentAngle - Callback to display current shoulder angle
 * @param {Function} setRepCount - Callback to update rep count
 * @param {string} side - Which arm to track: 'left' or 'right'
 * @param {string} userId - User identifier for adaptive tracking
 * @param {Object} userHistory - User's exercise history (optional)
 * @param {number} targetAngle - Override target angle (optional, uses adaptive if not provided)
 */
export const checkShoulderExercise = (
    landmarks, 
    onFeedbackUpdate, 
    setCurrentAngle, 
    setRepCount, 
    side = 'left',
    userId = null,
    userHistory = null,
    targetAngle = null
) => {
    if (!landmarks) {
        onFeedbackUpdate("Get in frame!");
        return;
    }

    // Calculate adaptive target if user data provided
    const standardTarget = 90; // Standard shoulder raise target
    let adaptiveTarget = targetAngle || standardTarget;
    
    if (userId && userHistory) {
        const personalTarget = calculatePersonalTarget(
            userId,
            shoulderExerciseConfig.name,
            userHistory,
            standardTarget
        );
        adaptiveTarget = personalTarget.recommendedTarget;
    }

    // Update target
    shoulderExerciseConfig.targets.targetShoulderAngle = adaptiveTarget;

    const { landmarks: lm } = shoulderExerciseConfig.jointInfo;
    
    // Select landmarks based on side
    const shoulderIdx = side === 'left' ? lm.leftShoulder : lm.rightShoulder;
    const elbowIdx = side === 'left' ? lm.leftElbow : lm.rightElbow;
    const hipIdx = side === 'left' ? lm.leftHip : lm.rightHip;

    // Check visibility
    const requiredLandmarks = [
        landmarks[shoulderIdx],
        landmarks[elbowIdx],
        landmarks[hipIdx]
    ];
    
    if (!visibilityCheck(requiredLandmarks)) {
        onFeedbackUpdate("Make sure your upper body is visible!");
        return;
    }

    // Calculate shoulder angle (hip-shoulder-elbow)
    // This measures arm elevation from the body
    const shoulderAngle = calculateAngle(
        landmarks[hipIdx],
        landmarks[shoulderIdx],
        landmarks[elbowIdx]
    );

    setCurrentAngle(Math.round(shoulderAngle));

    // Track angles for this rep
    if (currentState !== "DOWN") {
        repMinAngle = Math.min(repMinAngle === 0 ? shoulderAngle : repMinAngle, shoulderAngle);
        repMaxAngle = Math.max(repMaxAngle, shoulderAngle);
        
        // LSTM: Capture angle sequence during rep
        // Store multiple angles that could be used for quality assessment
        // For now, storing just shoulder angle (can be extended to include more joints)
        currentRepAngleSequence.push([shoulderAngle]);
    }

    // Determine transition
    const { downAngle, targetShoulderAngle: target, raisingThreshold } = shoulderExerciseConfig.targets;
    
    let transitionType = null;
    const isRaising = shoulderAngle > lastShoulderAngle; // Angle increasing = arm raising
    const isLowering = shoulderAngle < lastShoulderAngle; // Angle decreasing = arm lowering

    if (currentState === "DOWN" && isRaising && shoulderAngle > raisingThreshold) {
        transitionType = "raising";
    } else if (currentState === "RAISING") {
        if (shoulderAngle >= target) {
            transitionType = "targetReached";
        } else if (isLowering) {
            transitionType = "lowering";
        }
    } else if (currentState === "TARGET_REACHED" && isLowering) {
        transitionType = "lowering";
    } else if (currentState === "LOWERING" && shoulderAngle <= downAngle) {
        transitionType = "completed";
    }

    // Apply transition
    if (transitionType && shoulderExerciseConfig.transitions[currentState]?.[transitionType]) {
        const previousState = currentState;
        currentState = shoulderExerciseConfig.transitions[currentState][transitionType];
        
        const stateInfo = shoulderExerciseConfig.states[currentState];
        
        // Track rep completion for adaptive learning
        if (stateInfo.countRep) {
            repCount++;
            setRepCount(repCount);
            
            // LSTM: Predict movement quality for completed rep
            if (lstmEnabled && userId && currentRepAngleSequence.length > 5) {
                // Call LSTM API asynchronously (don't block UI)
                predictQuality(userId, currentRepAngleSequence)
                    .then(result => {
                        // Log prediction to console
                        logPrediction(result);
                        
                        // Update personalized target for next rep
                        personalizedTargetAngle = result.personalized_target_angle;
                        shoulderExerciseConfig.targets.targetShoulderAngle = personalizedTargetAngle;
                        
                        // Provide quality-based feedback
                        const qualityFeedback = getQualityFeedback(result.quality_score);
                        onFeedbackUpdate(qualityFeedback);
                        
                        // Store LSTM results with rep data
                        if (sessionReps.length > 0) {
                            const lastRep = sessionReps[sessionReps.length - 1];
                            lastRep.lstm_quality_score = result.quality_score;
                            lastRep.lstm_rep_rom = result.rep_rom;
                            lastRep.lstm_target = result.personalized_target_angle;
                        }
                    })
                    .catch(error => {
                        console.error('LSTM prediction failed:', error);
                    });
            }
            
            // Record this rep's performance
            if (userId) {
                const repData = {
                    angles: {
                        min: Math.round(repMinAngle),
                        max: Math.round(repMaxAngle),
                        avg: Math.round((repMinAngle + repMaxAngle) / 2)
                    },
                    timestamp: Date.now(),
                    duration: repStartTime ? Date.now() - repStartTime : 0,
                    success: repMaxAngle >= adaptiveTarget,
                    targetAngle: adaptiveTarget,
                    personalizedTarget: personalizedTargetAngle,
                    metadata: {
                        side,
                        shoulderAngle: Math.round(shoulderAngle)
                    }
                };
                
                trackRepPerformance(userId, shoulderExerciseConfig.name, repData);
                sessionReps.push(repData);
            }
            
            // Reset rep tracking
            repMinAngle = 0;
            repMaxAngle = 0;
            repStartTime = null;
            currentRepAngleSequence = []; // Reset angle sequence for next rep
        }
        
        // Start rep timer
        if (previousState === "DOWN" && currentState === "RAISING") {
            repStartTime = Date.now();
        }
        
        onFeedbackUpdate(stateInfo.feedback);
    }

    lastShoulderAngle = shoulderAngle;
    return currentState;
};

export const resetShoulderExercise = () => {
    currentState = "DOWN";
    repCount = 0;
    lastShoulderAngle = 30;
    sessionReps = [];
    repStartTime = null;
    repMinAngle = 0;
    repMaxAngle = 0;
    currentRepAngleSequence = [];
    personalizedTargetAngle = 90;
};

/**
 * End session and save performance data with rewards
 * 
 * @param {string} userId - User identifier
 * @param {Object} sessionInfo - Additional session metadata
 * @param {Object} currentUserRewards - Current user reward data
 * @param {Object} recentActivity - Recent activity stats
 * @param {number} userAge - User's age
 * @returns {Object} Session summary, recommendations, and rewards
 */
export const endShoulderSession = (userId, sessionInfo = {}, currentUserRewards = {}, recentActivity = {}, userAge = 40) => {
    if (!userId || sessionReps.length === 0) {
        return { error: "No session data to save" };
    }
    
    const sessionSummary = trackSessionPerformance(
        userId,
        shoulderExerciseConfig.name,
        sessionReps,
        {
            ...sessionInfo,
            endTime: Date.now()
        }
    );
    
    const recommendation = getProgressionRecommendation(
        userId,
        shoulderExerciseConfig.name,
        sessionSummary.userHistory
    );
    
    const rewardSummary = processSessionRewards(
        userId,
        {
            reps: sessionReps,
            sessionStats: sessionSummary.sessionStats,
            isPersonalBest: recommendation.status === 'progressing'
        },
        currentUserRewards,
        recentActivity
    );
    
    sessionReps = [];
    
    return {
        sessionSummary,
        recommendation,
        rewards: rewardSummary,
        message: `Session complete! ${repCount} reps, ${rewardSummary.rpEarned} RP earned!`
    };
};

/**
 * Alternative: External Rotation Exercise
 * 
 * This tracks shoulder external rotation (useful for rotator cuff exercises)
 * Measures angle between wrist-elbow-shoulder
 */
export const checkShoulderRotation = (
    landmarks,
    onFeedbackUpdate,
    setCurrentAngle,
    setRepCount,
    side = 'left',
    targetAngle = 90
) => {
    if (!landmarks) {
        onFeedbackUpdate("Get in frame!");
        return;
    }

    const { landmarks: lm } = shoulderExerciseConfig.jointInfo;
    
    const shoulderIdx = side === 'left' ? lm.leftShoulder : lm.rightShoulder;
    const elbowIdx = side === 'left' ? lm.leftElbow : lm.rightElbow;
    const wristIdx = side === 'left' ? lm.leftWrist : lm.rightWrist;

    const requiredLandmarks = [
        landmarks[shoulderIdx],
        landmarks[elbowIdx],
        landmarks[wristIdx]
    ];
    
    if (!visibilityCheck(requiredLandmarks)) {
        onFeedbackUpdate("Make sure your arm is visible!");
        return;
    }

    // Calculate rotation angle (shoulder-elbow-wrist)
    const rotationAngle = calculateAngle(
        landmarks[shoulderIdx],
        landmarks[elbowIdx],
        landmarks[wristIdx]
    );

    setCurrentAngle(Math.round(rotationAngle));
    
    // Provide simple feedback based on target
    if (rotationAngle >= targetAngle) {
        onFeedbackUpdate("Good rotation!");
    } else {
        onFeedbackUpdate("Rotate more!");
    }

    return rotationAngle;
};
