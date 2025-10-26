/**
 * Adaptive Learning Engine for Exercise Tracking
 * 
 * This module implements per-user adaptation, automatically adjusting exercise
 * targets based on individual performance and progress over time.
 * 
 * Future-ready for Reinforcement Learning (Option C) - all data collected here
 * can be used as training data for RL models.
 */

// ============================================================================
// Configuration
// ============================================================================

export const adaptiveConfig = {
    // Initial assessment phase
    initialAssessmentSessions: 3,      // Sessions needed to establish baseline
    minRepsForBaseline: 5,              // Minimum reps to establish baseline
    
    // Progression thresholds
    progressionThreshold: 5,            // Degrees of improvement to trigger level up
    regressionThreshold: 8,             // Degrees of decline to trigger level down
    
    // Consistency and stability
    consistencyWindowSize: 10,          // Number of reps to evaluate consistency
    minConsistencyScore: 0.7,           // Min consistency (0-1) for progression
    
    // Adaptation rates
    adaptationRate: 3,                  // Degrees to adjust target per level change
    minAdaptationRate: 2,               // Minimum adjustment
    maxAdaptationRate: 5,               // Maximum adjustment
    
    // Safety and pacing
    minSessionsBeforeProgression: 5,    // Prevent too-rapid progression
    plateauDetectionWindow: 10,         // Sessions without change = plateau
    maxTargetChangePerSession: 8,       // Maximum target change in one session
    
    // Difficulty levels
    difficultyLevels: {
        beginner: { modifier: 1.2, name: 'Beginner' },
        intermediate: { modifier: 1.0, name: 'Intermediate' },
        advanced: { modifier: 0.85, name: 'Advanced' },
        expert: { modifier: 0.7, name: 'Expert' }
    }
};

// ============================================================================
// User Performance Tracking
// ============================================================================

/**
 * Track individual rep performance
 * Stores detailed angle data for adaptive learning
 * 
 * @param {string} userId - User identifier
 * @param {string} exerciseName - Name of exercise (e.g., "Squat")
 * @param {Object} repData - Rep performance data
 * @returns {Object} Updated performance record
 */
export function trackRepPerformance(userId, exerciseName, repData) {
    const {
        repNumber,
        minAngle,
        maxAngle,
        avgAngle,
        timestamp = Date.now(),
        side = 'bilateral'
    } = repData;

    return {
        userId,
        exerciseName,
        repNumber,
        angles: {
            min: minAngle,
            max: maxAngle,
            avg: avgAngle,
            range: maxAngle - minAngle
        },
        side,
        timestamp,
        // Metadata for future RL training
        metadata: {
            timeOfDay: new Date(timestamp).getHours(),
            dayOfWeek: new Date(timestamp).getDay()
        }
    };
}

/**
 * Track complete exercise session
 * Aggregates rep data and calculates session statistics
 * 
 * @param {string} userId - User identifier
 * @param {string} exerciseName - Exercise name
 * @param {Array} reps - Array of rep data objects
 * @param {Object} sessionInfo - Additional session information
 * @returns {Object} Complete session record
 */
export function trackSessionPerformance(userId, exerciseName, reps, sessionInfo = {}) {
    if (!reps || reps.length === 0) {
        throw new Error('Session must contain at least one rep');
    }

    // Calculate session statistics
    const angles = reps.map(r => r.angles.avg);
    const avgAngle = angles.reduce((a, b) => a + b, 0) / angles.length;
    const bestAngle = Math.min(...angles);
    const worstAngle = Math.max(...angles);
    
    // Calculate consistency (inverse of coefficient of variation)
    const stdDev = calculateStdDev(angles);
    const consistency = 1 - (stdDev / avgAngle);

    return {
        userId,
        exerciseName,
        sessionId: `session_${Date.now()}`,
        date: new Date().toISOString().split('T')[0],
        timestamp: Date.now(),
        reps: reps,
        sessionStats: {
            totalReps: reps.length,
            avgAngle: Math.round(avgAngle * 10) / 10,
            bestAngle: Math.round(bestAngle),
            worstAngle: Math.round(worstAngle),
            rangeOfMotion: worstAngle - bestAngle,
            consistency: Math.round(consistency * 100) / 100,
            completionRate: sessionInfo.targetReps ? reps.length / sessionInfo.targetReps : 1.0
        },
        sessionInfo: {
            targetReps: sessionInfo.targetReps || reps.length,
            targetAngle: sessionInfo.targetAngle,
            duration: sessionInfo.duration,
            userNotes: sessionInfo.notes || ''
        }
    };
}

// ============================================================================
// Baseline Assessment
// ============================================================================

/**
 * Calculate initial baseline target for new users
 * Uses first few sessions to establish achievable starting point
 * 
 * @param {Array} initialSessions - First 3-5 sessions of data
 * @param {number} standardTarget - Standard/ideal target angle
 * @returns {Object} Baseline assessment with recommended target
 */
export function calculateBaseline(initialSessions, standardTarget = 90) {
    if (!initialSessions || initialSessions.length < adaptiveConfig.initialAssessmentSessions) {
        return {
            status: 'incomplete',
            sessionsNeeded: adaptiveConfig.initialAssessmentSessions - (initialSessions?.length || 0),
            message: 'Complete more sessions to establish baseline',
            recommendedTarget: standardTarget * 1.2 // Conservative starting point
        };
    }

    // Aggregate all reps from initial sessions
    const allAngles = initialSessions.flatMap(session => 
        session.reps.map(rep => rep.angles.avg)
    );

    const avgAngle = allAngles.reduce((a, b) => a + b, 0) / allAngles.length;
    const bestAngle = Math.min(...allAngles);
    const consistency = 1 - (calculateStdDev(allAngles) / avgAngle);

    // Determine initial difficulty level
    let difficultyLevel;
    if (avgAngle >= standardTarget * 1.3) {
        difficultyLevel = 'beginner';
    } else if (avgAngle >= standardTarget * 1.1) {
        difficultyLevel = 'intermediate';
    } else {
        difficultyLevel = 'advanced';
    }

    // Set achievable but challenging target
    const recommendedTarget = Math.round(avgAngle - 5); // Slightly better than average

    return {
        status: 'complete',
        baselineStats: {
            avgAngle: Math.round(avgAngle * 10) / 10,
            bestAngle: Math.round(bestAngle),
            consistency: Math.round(consistency * 100) / 100,
            totalReps: allAngles.length
        },
        difficultyLevel,
        recommendedTarget,
        message: `Baseline established! Starting at ${difficultyLevel} level.`
    };
}

// ============================================================================
// Adaptive Target Calculation
// ============================================================================

/**
 * Calculate personalized target angle based on user history
 * This is the core adaptive function called before each exercise session
 * 
 * @param {string} userId - User identifier
 * @param {string} exerciseName - Exercise name
 * @param {Object} userHistory - User's complete performance history
 * @param {number} standardTarget - Standard target angle (default 90)
 * @returns {Object} Adaptive target and reasoning
 */
export function calculatePersonalTarget(userId, exerciseName, userHistory, standardTarget = 90) {
    const {
        sessions = [],
        currentLevel = {},
        progressMetrics = {}
    } = userHistory;

    // If no history, use baseline approach
    if (sessions.length < adaptiveConfig.initialAssessmentSessions) {
        const baseline = calculateBaseline(sessions, standardTarget);
        return {
            target: baseline.recommendedTarget || standardTarget * 1.2,
            confidence: 'low',
            reason: 'Establishing baseline',
            baseline
        };
    }

    // Get recent performance (last 5 sessions)
    const recentSessions = sessions.slice(-5);
    const recentAngles = recentSessions.flatMap(s => s.reps.map(r => r.angles.avg));
    const recentAvg = recentAngles.reduce((a, b) => a + b, 0) / recentAngles.length;
    const recentBest = Math.min(...recentAngles);
    const recentConsistency = 1 - (calculateStdDev(recentAngles) / recentAvg);

    // Current target from user profile
    const currentTarget = currentLevel.personalTarget || standardTarget;

    // Calculate performance relative to current target
    const performanceGap = recentAvg - currentTarget;
    
    let newTarget = currentTarget;
    let reason = 'Maintaining current level';
    let adjustment = 0;

    // Decision logic for target adjustment
    if (recentConsistency >= adaptiveConfig.minConsistencyScore) {
        // User is consistent - check if ready for progression
        
        if (performanceGap < -adaptiveConfig.progressionThreshold) {
            // User is exceeding target consistently - make it harder
            adjustment = -adaptiveConfig.adaptationRate;
            reason = 'Excellent progress! Increasing challenge.';
        } else if (performanceGap > adaptiveConfig.regressionThreshold) {
            // User is struggling - make it easier
            adjustment = adaptiveConfig.adaptationRate;
            reason = 'Adjusting for better success rate.';
        } else {
            // User is in the sweet spot
            reason = 'Perfect! Keep up the consistency.';
        }
    } else {
        // User is inconsistent - focus on consistency before progression
        if (performanceGap > adaptiveConfig.regressionThreshold) {
            adjustment = Math.min(adaptiveConfig.adaptationRate, performanceGap / 2);
            reason = 'Easing difficulty to build consistency.';
        } else {
            reason = 'Focus on consistency at current level.';
        }
    }

    // Apply adjustment with safety limits
    newTarget = Math.round(currentTarget + adjustment);
    
    // Don't change too drastically in one session
    const maxChange = adaptiveConfig.maxTargetChangePerSession;
    if (Math.abs(newTarget - currentTarget) > maxChange) {
        newTarget = currentTarget + (adjustment > 0 ? maxChange : -maxChange);
    }

    // Don't go easier than beginner or harder than expert
    const minTarget = standardTarget * 0.7;  // Expert level
    const maxTarget = standardTarget * 1.3;  // Beginner level
    newTarget = Math.max(minTarget, Math.min(maxTarget, newTarget));

    return {
        target: newTarget,
        previousTarget: currentTarget,
        adjustment: newTarget - currentTarget,
        confidence: recentConsistency >= adaptiveConfig.minConsistencyScore ? 'high' : 'medium',
        reason,
        metrics: {
            recentAvg: Math.round(recentAvg * 10) / 10,
            recentBest: Math.round(recentBest),
            consistency: Math.round(recentConsistency * 100) / 100,
            performanceGap: Math.round(performanceGap)
        }
    };
}

// ============================================================================
// Difficulty Level Management
// ============================================================================

/**
 * Adjust user's difficulty level based on performance
 * 
 * @param {string} userId - User identifier
 * @param {string} exerciseName - Exercise name
 * @param {Object} recentPerformance - Recent performance data
 * @returns {Object} Difficulty adjustment recommendation
 */
export function adjustDifficulty(userId, exerciseName, recentPerformance) {
    const {
        currentLevel = 'intermediate',
        recentSessions = [],
        personalTarget,
        standardTarget = 90
    } = recentPerformance;

    // Calculate how close user is to standard target
    const targetRatio = personalTarget / standardTarget;
    const levels = Object.keys(adaptiveConfig.difficultyLevels);
    
    let newLevel = currentLevel;
    let shouldChange = false;

    // Check if user has been at current level long enough
    const sessionsAtLevel = recentSessions.filter(s => 
        s.difficultyLevel === currentLevel
    ).length;

    if (sessionsAtLevel >= adaptiveConfig.minSessionsBeforeProgression) {
        // Determine appropriate level based on target ratio
        if (targetRatio <= 0.75 && currentLevel !== 'expert') {
            newLevel = levels[Math.min(levels.indexOf(currentLevel) + 1, levels.length - 1)];
            shouldChange = true;
        } else if (targetRatio >= 1.25 && currentLevel !== 'beginner') {
            newLevel = levels[Math.max(levels.indexOf(currentLevel) - 1, 0)];
            shouldChange = true;
        }
    }

    return {
        currentLevel,
        recommendedLevel: newLevel,
        shouldChange,
        levelInfo: adaptiveConfig.difficultyLevels[newLevel],
        message: shouldChange 
            ? `Ready to level up to ${newLevel}!`
            : `Continue building strength at ${currentLevel} level`
    };
}

// ============================================================================
// Progression Recommendations
// ============================================================================

/**
 * Generate progression recommendation for user
 * Suggests next steps based on performance trends
 * 
 * @param {string} userId - User identifier
 * @param {string} exerciseName - Exercise name
 * @param {Object} userHistory - Complete user history
 * @returns {Object} Progression recommendation
 */
export function getProgressionRecommendation(userId, exerciseName, userHistory) {
    const { sessions = [], progressMetrics = {} } = userHistory;

    if (sessions.length < 10) {
        return {
            type: 'continue',
            message: 'Keep practicing to build a solid foundation',
            nextMilestone: '10 total sessions',
            sessionsToGo: 10 - sessions.length
        };
    }

    // Check for plateau
    const last10Sessions = sessions.slice(-10);
    const angles = last10Sessions.map(s => s.sessionStats.avgAngle);
    const improvement = angles[0] - angles[angles.length - 1];

    if (Math.abs(improvement) < 2) {
        // Plateau detected
        return {
            type: 'plateau',
            message: 'Consider trying a variation or taking a rest day',
            suggestions: [
                'Try a different exercise targeting the same muscle group',
                'Take 2-3 days rest for recovery',
                'Focus on form quality over depth',
                'Consult with a physical therapist'
            ]
        };
    }

    // Check if ready for next challenge
    const currentTarget = userHistory.currentLevel?.personalTarget;
    const standardTarget = 90; // This should come from exercise config
    
    if (currentTarget && currentTarget <= standardTarget * 1.05) {
        return {
            type: 'advanced_ready',
            message: 'You\'ve mastered the standard! Ready for advanced challenges?',
            suggestions: [
                'Try deeper range of motion',
                'Add tempo variations (slow descent)',
                'Attempt single-leg variations',
                'Increase rep count'
            ]
        };
    }

    // General progression
    return {
        type: 'progressing',
        message: 'Great progress! Keep up the consistent work.',
        improvementRate: `${Math.round(improvement / 10 * 100)}% over last 10 sessions`,
        nextMilestone: `Reach ${Math.round(currentTarget - 5)}° average`
    };
}

// ============================================================================
// Utility Functions
// ============================================================================

/**
 * Calculate standard deviation of an array
 */
function calculateStdDev(values) {
    const avg = values.reduce((a, b) => a + b, 0) / values.length;
    const squareDiffs = values.map(value => Math.pow(value - avg, 2));
    const avgSquareDiff = squareDiffs.reduce((a, b) => a + b, 0) / values.length;
    return Math.sqrt(avgSquareDiff);
}

/**
 * Calculate moving average
 */
export function calculateMovingAverage(values, windowSize) {
    if (values.length < windowSize) return values;
    
    const result = [];
    for (let i = windowSize - 1; i < values.length; i++) {
        const window = values.slice(i - windowSize + 1, i + 1);
        const avg = window.reduce((a, b) => a + b, 0) / windowSize;
        result.push(avg);
    }
    return result;
}

/**
 * Detect if user is experiencing a plateau
 */
export function detectPlateau(sessions) {
    if (sessions.length < adaptiveConfig.plateauDetectionWindow) {
        return { isPlateau: false, confidence: 0 };
    }

    const recentSessions = sessions.slice(-adaptiveConfig.plateauDetectionWindow);
    const angles = recentSessions.map(s => s.sessionStats.avgAngle);
    const stdDev = calculateStdDev(angles);
    const avg = angles.reduce((a, b) => a + b, 0) / angles.length;
    
    // Low standard deviation + no improvement = plateau
    const coefficientOfVariation = stdDev / avg;
    const isPlateau = coefficientOfVariation < 0.05; // Very little variation
    
    return {
        isPlateau,
        confidence: isPlateau ? 1 - coefficientOfVariation : 0,
        recommendation: isPlateau ? 'Consider changing routine or resting' : 'Continue current program'
    };
}

// Export all functions
export default {
    // Config
    adaptiveConfig,
    
    // Tracking
    trackRepPerformance,
    trackSessionPerformance,
    
    // Assessment
    calculateBaseline,
    calculatePersonalTarget,
    
    // Adaptation
    adjustDifficulty,
    getProgressionRecommendation,
    
    // Analytics
    calculateMovingAverage,
    detectPlateau
};
