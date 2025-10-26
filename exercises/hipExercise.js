/**
 * Hip Exercise Example: Hip Flexion / Leg Raise (with Adaptive Learning & Rewards)
 * 
 * This demonstrates how to track hip angle for exercises like leg raises,
 * hip flexion tests, or standing marches with personalized adaptive targets
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

/**
 * Hip Exercise Configuration
 */
export const hipExerciseConfig = {
    name: "Hip Flexion",
    
    states: {
        STANDING: { 
            feedback: "Lift your leg!", 
            audio: false, 
            countRep: false, 
            color: "yellow" 
        },
        LIFTING: { 
            feedback: "Keep going!", 
            audio: false, 
            countRep: false, 
            color: "yellow" 
        },
        TARGET_REACHED: { 
            feedback: "Perfect! Now lower it.", 
            audio: true, 
            countRep: false, 
            color: "green" 
        },
        LOWERING: { 
            feedback: "Good control!", 
            audio: false, 
            countRep: false, 
            color: "blue" 
        },
        COMPLETED: { 
            feedback: "Rep complete!", 
            audio: true, 
            countRep: true, 
            color: "green" 
        }
    },

    transitions: {
        STANDING: {
            lifting: "LIFTING"
        },
        LIFTING: {
            targetReached: "TARGET_REACHED",
            lowering: "STANDING"
        },
        TARGET_REACHED: {
            lowering: "LOWERING"
        },
        LOWERING: {
            completed: "COMPLETED"
        },
        COMPLETED: {
            lifting: "LIFTING"
        }
    },

    jointInfo: {
        landmarks: {
            leftShoulder: 11,
            leftHip: 23,
            leftKnee: 25,
            rightShoulder: 12,
            rightHip: 24,
            rightKnee: 26
        }
    },

    targets: {
        standingHipAngle: 170,    // Nearly straight when standing
        targetHipAngle: 90,       // 90° hip flexion (leg raised to horizontal)
        liftingThreshold: 150     // Angle when starting to lift
    }
};

let currentState = "STANDING";
let repCount = 0;
let lastHipAngle = 180;
let sessionReps = [];
let repStartTime = null;
let repMinAngle = 180;
let repMaxAngle = 0;

/**
 * Check hip exercise form (with adaptive learning)
 * 
 * @param {Array} landmarks - MediaPipe pose landmarks
 * @param {Function} onFeedbackUpdate - Callback for feedback
 * @param {Function} setCurrentAngle - Callback to display current hip angle
 * @param {Function} setRepCount - Callback to update rep count
 * @param {string} side - Which leg to track: 'left' or 'right'
 * @param {string} userId - User identifier for adaptive tracking
 * @param {Object} userHistory - User's exercise history (optional)
 * @param {number} targetHipAngle - Override target angle (optional, uses adaptive if not provided)
 */
export const checkHipExercise = (
    landmarks, 
    onFeedbackUpdate, 
    setCurrentAngle, 
    setRepCount, 
    side = 'left',
    userId = null,
    userHistory = null,
    targetHipAngle = null
) => {
    if (!landmarks) {
        onFeedbackUpdate("Get in frame!");
        return;
    }

    // Calculate adaptive target if user data provided
    const standardTarget = 90; // Standard hip flexion target
    let adaptiveTarget = targetHipAngle || standardTarget;
    
    if (userId && userHistory) {
        const personalTarget = calculatePersonalTarget(
            userId,
            hipExerciseConfig.name,
            userHistory,
            standardTarget
        );
        adaptiveTarget = personalTarget.recommendedTarget;
    }

    // Update target
    hipExerciseConfig.targets.targetHipAngle = adaptiveTarget;

    const { landmarks: lm } = hipExerciseConfig.jointInfo;
    
    // Select landmarks based on side
    const shoulderIdx = side === 'left' ? lm.leftShoulder : lm.rightShoulder;
    const hipIdx = side === 'left' ? lm.leftHip : lm.rightHip;
    const kneeIdx = side === 'left' ? lm.leftKnee : lm.rightKnee;

    // Check visibility
    const requiredLandmarks = [
        landmarks[shoulderIdx],
        landmarks[hipIdx],
        landmarks[kneeIdx]
    ];
    
    if (!visibilityCheck(requiredLandmarks)) {
        onFeedbackUpdate("Make sure your body is visible!");
        return;
    }

    // Calculate hip angle (shoulder-hip-knee)
    const hipAngle = calculateAngle(
        landmarks[shoulderIdx],
        landmarks[hipIdx],
        landmarks[kneeIdx]
    );

    setCurrentAngle(Math.round(hipAngle));

    // Track angles for this rep
    if (currentState !== "STANDING") {
        repMinAngle = Math.min(repMinAngle, hipAngle);
        repMaxAngle = Math.max(repMaxAngle, hipAngle);
    }

    // Determine transition
    const { standingHipAngle, targetHipAngle: target, liftingThreshold } = hipExerciseConfig.targets;
    
    let transitionType = null;
    const isDescending = hipAngle > lastHipAngle; // Angle increasing = leg lowering
    const isAscending = hipAngle < lastHipAngle;  // Angle decreasing = leg lifting

    if (currentState === "STANDING" && isAscending && hipAngle < liftingThreshold) {
        transitionType = "lifting";
    } else if (currentState === "LIFTING") {
        if (hipAngle <= target) {
            transitionType = "targetReached";
        } else if (isDescending) {
            transitionType = "lowering";
        }
    } else if (currentState === "TARGET_REACHED" && isDescending) {
        transitionType = "lowering";
    } else if (currentState === "LOWERING" && hipAngle >= standingHipAngle) {
        transitionType = "completed";
    }

    // Apply transition
    if (transitionType && hipExerciseConfig.transitions[currentState]?.[transitionType]) {
        const previousState = currentState;
        currentState = hipExerciseConfig.transitions[currentState][transitionType];
        
        const stateInfo = hipExerciseConfig.states[currentState];
        
        // Track rep completion for adaptive learning
        if (stateInfo.countRep) {
            repCount++;
            setRepCount(repCount);
            
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
                    success: repMinAngle <= adaptiveTarget,
                    targetAngle: adaptiveTarget,
                    metadata: {
                        side,
                        hipAngle: Math.round(hipAngle)
                    }
                };
                
                trackRepPerformance(userId, hipExerciseConfig.name, repData);
                sessionReps.push(repData);
            }
            
            // Reset rep tracking
            repMinAngle = 180;
            repMaxAngle = 0;
            repStartTime = null;
        }
        
        // Start rep timer
        if (previousState === "STANDING" && currentState === "LIFTING") {
            repStartTime = Date.now();
        }
        
        onFeedbackUpdate(stateInfo.feedback);
    }

    lastHipAngle = hipAngle;
    return currentState;
};

export const resetHipExercise = () => {
    currentState = "STANDING";
    repCount = 0;
    lastHipAngle = 180;
    sessionReps = [];
    repStartTime = null;
    repMinAngle = 180;
    repMaxAngle = 0;
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
export const endHipSession = (userId, sessionInfo = {}, currentUserRewards = {}, recentActivity = {}, userAge = 40) => {
    if (!userId || sessionReps.length === 0) {
        return { error: "No session data to save" };
    }
    
    const sessionSummary = trackSessionPerformance(
        userId,
        hipExerciseConfig.name,
        sessionReps,
        {
            ...sessionInfo,
            endTime: Date.now()
        }
    );
    
    const recommendation = getProgressionRecommendation(
        userId,
        hipExerciseConfig.name,
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
