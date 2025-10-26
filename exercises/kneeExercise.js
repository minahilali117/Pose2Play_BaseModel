/**
 * Knee Exercise Example: Squat (with Adaptive Learning & Rewards)
 * 
 * This demonstrates how to build a rule-based exercise checker for knee exercises.
 * The system uses a Finite State Machine (FSM) to track exercise progression,
 * integrates adaptive learning to personalize targets, and awards Recovery Points (RP)
 * for motivation.
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
    calculateRepRP,
    processSessionRewards 
} from '../utils/rewardSystem.js';
import {
    getRepFeedback
} from '../utils/motivationEngine.js';

/**
 * Squat Exercise Configuration
 * 
 * This object defines:
 * - States: Different phases of the exercise
 * - Transitions: Rules for moving between states
 * - Joint info: Which body landmarks to track
 * - Targets: Angle thresholds for correct form
 */
export const squatExerciseConfig = {
    name: "Squat",
    
    // Define all possible states
    states: {
        STANDING: { 
            feedback: "Please Begin Rep!", 
            audio: false, 
            countRep: false, 
            color: "yellow" 
        },
        DESCENDING: { 
            feedback: "Go Down Lower!", 
            audio: true, 
            countRep: false, 
            color: "yellow" 
        },
        SQUATTING: { 
            feedback: "Excellent!", 
            audio: true, 
            countRep: false, 
            color: "green" 
        },
        FINISHED: { 
            feedback: "Excellent!", 
            audio: false, 
            countRep: true, 
            color: "green" 
        }
    },

    // Define state transitions
    transitions: {
        STANDING: {
            descending: "DESCENDING",
        },
        DESCENDING: {
            hitTarget: "SQUATTING",
            finishing: "STANDING",
        },
        SQUATTING: {
            finishing: "FINISHED",
        },
        FINISHED: {
            descending: "DESCENDING",
        }
    },

    // Define which body landmarks to track
    jointInfo: {
        landmarks: {
            leftHip: 23,
            leftKnee: 25,
            leftAnkle: 27,
            rightHip: 24,
            rightKnee: 26,
            rightAnkle: 28
        }
    },

    // Define angle thresholds
    targets: {
        thresholdKneeAngle: 160, // Angle when starting to descend
        targetKneeAngle: 90,      // Target squat depth
    }
};

/**
 * Check squat form and update state (with adaptive learning)
 * 
 * @param {Array} landmarks - MediaPipe pose landmarks (33 points)
 * @param {Function} onFeedbackUpdate - Callback to update UI feedback
 * @param {Function} setCurrentAngle - Callback to display current knee angle
 * @param {Function} setRepCount - Callback to update rep counter
 * @param {string} userId - User identifier for adaptive tracking
 * @param {Object} userHistory - User's exercise history (optional)
 * @param {number} targetKneeAngle - Override target angle (optional, uses adaptive if not provided)
 */
let currentState = "STANDING";
let repCount = 0;
let sessionReps = []; // Track reps for this session
let repStartTime = null;
let repMinAngle = 180;
let repMaxAngle = 0;

export const checkSquat = (landmarks, onFeedbackUpdate, setCurrentAngle, setRepCount, userId = null, userHistory = null, targetKneeAngle = null) => {
    if (!landmarks) {
        onFeedbackUpdate("Get in frame!");
        return;
    }

    // Calculate adaptive target if user data provided
    const standardTarget = 90; // Standard squat target
    let adaptiveTarget = targetKneeAngle || standardTarget;
    
    if (userId && userHistory) {
        const personalTarget = calculatePersonalTarget(
            userId,
            squatExerciseConfig.name,
            userHistory,
            standardTarget
        );
        adaptiveTarget = personalTarget.recommendedTarget;
    }

    // Update target
    squatExerciseConfig.targets.targetKneeAngle = adaptiveTarget;

    // Get landmarks
    const { leftHip, leftKnee, leftAnkle, rightHip, rightKnee, rightAnkle } = squatExerciseConfig.jointInfo.landmarks;

    // Check visibility
    const requiredLandmarks = [
        landmarks[leftHip], landmarks[leftKnee], landmarks[leftAnkle],
        landmarks[rightHip], landmarks[rightKnee], landmarks[rightAnkle]
    ];
    
    if (!visibilityCheck(requiredLandmarks)) {
        onFeedbackUpdate("Make sure legs are visible!");
        return;
    }

    // Calculate knee angles
    const leftKneeAngle = calculateAngle(
        landmarks[leftHip],
        landmarks[leftKnee],
        landmarks[leftAnkle]
    );
    
    const rightKneeAngle = calculateAngle(
        landmarks[rightHip],
        landmarks[rightKnee],
        landmarks[rightAnkle]
    );

    // Use the smaller (more bent) knee angle
    const kneeAngle = Math.min(leftKneeAngle, rightKneeAngle);
    setCurrentAngle(Math.round(kneeAngle));

    // Track angles for this rep
    if (currentState !== "STANDING") {
        repMinAngle = Math.min(repMinAngle, kneeAngle);
        repMaxAngle = Math.max(repMaxAngle, kneeAngle);
    }

    // Determine transition based on knee angle
    const thresholdAngle = squatExerciseConfig.targets.thresholdKneeAngle;
    const targetAngle = squatExerciseConfig.targets.targetKneeAngle;

    let transitionType = null;

    if (kneeAngle < targetAngle) {
        transitionType = "hitTarget";
    } else if (kneeAngle < thresholdAngle) {
        transitionType = "descending";
    } else if (kneeAngle > thresholdAngle) {
        transitionType = "finishing";
    }

    // Apply state transition
    if (transitionType && squatExerciseConfig.transitions[currentState]?.[transitionType]) {
        const previousState = currentState;
        currentState = squatExerciseConfig.transitions[currentState][transitionType];
        
        const stateInfo = squatExerciseConfig.states[currentState];
        
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
                        leftKnee: Math.round(leftKneeAngle),
                        rightKnee: Math.round(rightKneeAngle)
                    }
                };
                
                trackRepPerformance(userId, squatExerciseConfig.name, repData);
                sessionReps.push(repData);
            }
            
            // Reset rep tracking
            repMinAngle = 180;
            repMaxAngle = 0;
            repStartTime = null;
        }
        
        // Start rep timer
        if (previousState === "STANDING" && currentState === "DESCENDING") {
            repStartTime = Date.now();
        }
        
        // Update feedback
        onFeedbackUpdate(stateInfo.feedback);
    }

    return currentState;
};

/**
 * Reset exercise state
 */
export const resetSquat = () => {
    currentState = "STANDING";
    repCount = 0;
    sessionReps = [];
    repStartTime = null;
    repMinAngle = 180;
    repMaxAngle = 0;
};

/**
 * End session and save performance data with reward calculation
 * Call this when user finishes their workout
 * 
 * @param {string} userId - User identifier
 * @param {Object} sessionInfo - Additional session metadata
 * @param {Object} currentUserRewards - Current user reward data from database
 * @param {Object} recentActivity - User's recent activity stats
 * @param {number} userAge - User's age for age-appropriate rewards (default 40)
 * @returns {Object} Session summary, recommendations, and rewards earned
 */
export const endSquatSession = (userId, sessionInfo = {}, currentUserRewards = {}, recentActivity = {}, userAge = 40) => {
    if (!userId || sessionReps.length === 0) {
        return { error: "No session data to save" };
    }
    
    // Track session performance (adaptive learning)
    const sessionSummary = trackSessionPerformance(
        userId,
        squatExerciseConfig.name,
        sessionReps,
        {
            ...sessionInfo,
            endTime: Date.now()
        }
    );
    
    // Get progression recommendation
    const recommendation = getProgressionRecommendation(
        userId,
        squatExerciseConfig.name,
        sessionSummary.userHistory
    );
    
    // Calculate rewards earned (gamification)
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
    
    // Reset session
    sessionReps = [];
    
    return {
        sessionSummary,
        recommendation,
        rewards: rewardSummary,
        message: `Session complete! ${repCount} reps, ${rewardSummary.rpEarned} RP earned!`
    };
};
