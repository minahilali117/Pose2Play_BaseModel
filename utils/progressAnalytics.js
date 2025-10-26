/**
 * Progress Analytics for Adaptive Exercise Tracking
 * 
 * Advanced analytics functions for tracking user progress, predicting outcomes,
 * and generating insights for personalized exercise recommendations.
 */

// ============================================================================
// Improvement Rate Calculation
// ============================================================================

/**
 * Calculate user's improvement rate over time
 * Returns percentage improvement and trend direction
 * 
 * @param {Array} sessionHistory - Array of session objects
 * @param {number} windowSize - Number of sessions to analyze (default: all)
 * @returns {Object} Improvement metrics
 */
export function calculateImprovementRate(sessionHistory, windowSize = null) {
    if (!sessionHistory || sessionHistory.length < 2) {
        return {
            improvementRate: 0,
            trend: 'insufficient_data',
            message: 'Need at least 2 sessions to calculate improvement'
        };
    }

    const sessions = windowSize 
        ? sessionHistory.slice(-windowSize)
        : sessionHistory;

    // Get angles over time
    const angles = sessions.map(s => s.sessionStats.avgAngle);
    const dates = sessions.map(s => new Date(s.date).getTime());

    // Calculate linear regression for trend
    const n = angles.length;
    const sumX = dates.reduce((a, b) => a + b, 0);
    const sumY = angles.reduce((a, b) => a + b, 0);
    const sumXY = dates.reduce((sum, x, i) => sum + x * angles[i], 0);
    const sumXX = dates.reduce((sum, x) => sum + x * x, 0);

    const slope = (n * sumXY - sumX * sumY) / (n * sumXX - sumX * sumX);
    
    // Negative slope = improvement (lower angles are better)
    const improvementRate = -slope * 86400000 * 7; // Convert to degrees per week
    
    // Determine trend
    let trend;
    if (Math.abs(improvementRate) < 0.5) {
        trend = 'stable';
    } else if (improvementRate > 0) {
        trend = 'improving';
    } else {
        trend = 'declining';
    }

    // Calculate R-squared for trend confidence
    const meanY = sumY / n;
    const ssTotal = angles.reduce((sum, y) => sum + Math.pow(y - meanY, 2), 0);
    const predicted = dates.map((x, i) => {
        const b = (sumY - slope * sumX) / n;
        return slope * x + b;
    });
    const ssResidual = angles.reduce((sum, y, i) => 
        sum + Math.pow(y - predicted[i], 2), 0
    );
    const rSquared = 1 - (ssResidual / ssTotal);

    return {
        improvementRate: Math.round(improvementRate * 10) / 10,
        trend,
        confidence: Math.round(rSquared * 100),
        totalImprovement: Math.round(angles[0] - angles[angles.length - 1]),
        averagePerSession: Math.round((angles[0] - angles[angles.length - 1]) / n * 10) / 10,
        message: getTrendMessage(trend, improvementRate)
    };
}

function getTrendMessage(trend, rate) {
    if (trend === 'improving') {
        return `Improving at ${Math.abs(rate).toFixed(1)}° per week - excellent!`;
    } else if (trend === 'declining') {
        return `Performance declining ${Math.abs(rate).toFixed(1)}° per week - consider rest`;
    } else {
        return 'Performance stable - ready for next challenge?';
    }
}

// ============================================================================
// Predictive Analytics
// ============================================================================

/**
 * Predict next target angle based on current performance trends
 * Uses historical data to forecast optimal progression
 * 
 * @param {Object} currentPerformance - Current user stats
 * @param {Array} historicalData - Past session data
 * @returns {Object} Prediction with confidence intervals
 */
export function predictNextTarget(currentPerformance, historicalData) {
    const {
        currentTarget,
        recentAverage,
        consistency
    } = currentPerformance;

    if (!historicalData || historicalData.length < 5) {
        return {
            predictedTarget: currentTarget,
            confidence: 'low',
            message: 'Need more data for accurate prediction'
        };
    }

    // Calculate improvement trend
    const { improvementRate, trend } = calculateImprovementRate(historicalData, 10);
    
    // Predict based on trend and consistency
    let predictedTarget = currentTarget;
    let confidenceLevel = 'low';

    if (consistency > 0.8 && trend === 'improving') {
        // User is consistent and improving - aggressive progression
        predictedTarget = Math.round(currentTarget - improvementRate / 2);
        confidenceLevel = 'high';
    } else if (consistency > 0.7 && trend === 'improving') {
        // Moderate progression
        predictedTarget = Math.round(currentTarget - improvementRate / 4);
        confidenceLevel = 'medium';
    } else if (consistency < 0.6 || trend === 'declining') {
        // Maintain or ease off
        predictedTarget = Math.round(currentTarget + Math.abs(improvementRate) / 4);
        confidenceLevel = 'medium';
    } else {
        // Stable - maintain
        confidenceLevel = 'medium';
    }

    // Safety bounds
    const minSafeTarget = Math.round(recentAverage - 10);
    const maxSafeTarget = Math.round(recentAverage + 5);
    predictedTarget = Math.max(minSafeTarget, Math.min(maxSafeTarget, predictedTarget));

    return {
        predictedTarget,
        currentTarget,
        change: predictedTarget - currentTarget,
        confidence: confidenceLevel,
        reasoning: getpredictionReasoning(trend, consistency, improvementRate),
        safeRange: {
            min: minSafeTarget,
            max: maxSafeTarget
        }
    };
}

function getpredictionReasoning(trend, consistency, rate) {
    if (trend === 'improving' && consistency > 0.8) {
        return 'Strong consistent improvement - ready for harder challenge';
    } else if (trend === 'improving' && consistency > 0.6) {
        return 'Improving but variable - moderate progression recommended';
    } else if (trend === 'stable') {
        return 'Performance stable - maintain current difficulty';
    } else {
        return 'Performance variable - focus on consistency';
    }
}

// ============================================================================
// Readiness Assessment
// ============================================================================

/**
 * Assess if user is ready for progression to next level
 * 
 * @param {Object} recentPerformance - Last 5-10 sessions
 * @returns {Object} Readiness assessment
 */
export function assessReadinessForProgression(recentPerformance) {
    const {
        sessions = [],
        currentTarget,
        personalBest,
        consistency,
        consecutiveSuccesses = 0
    } = recentPerformance;

    if (sessions.length < 5) {
        return {
            ready: false,
            confidence: 0,
            reason: 'Need at least 5 sessions at current level',
            requiredSessions: 5 - sessions.length
        };
    }

    // Criteria for progression
    const criteria = {
        consistencyMet: consistency >= 0.75,
        performanceGap: personalBest < currentTarget - 5,
        consecutiveMet: consecutiveSuccesses >= 3,
        recentTrend: calculateImprovementRate(sessions, 5).trend === 'improving'
    };

    const metCount = Object.values(criteria).filter(Boolean).length;
    const readinessScore = metCount / Object.keys(criteria).length;

    return {
        ready: readinessScore >= 0.75,
        readinessScore: Math.round(readinessScore * 100),
        criteria,
        metCriteria: metCount,
        totalCriteria: Object.keys(criteria).length,
        recommendation: getReadinessRecommendation(readinessScore, criteria)
    };
}

function getReadinessRecommendation(score, criteria) {
    if (score >= 0.75) {
        return 'Ready for next level! Time to increase the challenge.';
    } else if (score >= 0.5) {
        const missing = Object.entries(criteria)
            .filter(([_, met]) => !met)
            .map(([key, _]) => key);
        return `Almost there! Work on: ${missing.join(', ')}`;
    } else {
        return 'Focus on consistency at current level before progressing.';
    }
}

// ============================================================================
// Progress Reports
// ============================================================================

/**
 * Generate comprehensive progress report for user
 * 
 * @param {string} userId - User identifier
 * @param {string} exerciseName - Exercise name
 * @param {string} timeRange - 'week', 'month', 'all'
 * @param {Object} userData - Complete user data
 * @returns {Object} Detailed progress report
 */
export function generateProgressReport(userId, exerciseName, timeRange, userData) {
    const { sessions = [], progressMetrics = {}, currentLevel = {} } = userData;

    // Filter sessions by time range
    const now = Date.now();
    const ranges = {
        week: 7 * 24 * 60 * 60 * 1000,
        month: 30 * 24 * 60 * 60 * 1000,
        all: Infinity
    };
    
    const rangeMs = ranges[timeRange] || ranges.all;
    const filteredSessions = sessions.filter(s => 
        now - new Date(s.date).getTime() <= rangeMs
    );

    if (filteredSessions.length === 0) {
        return {
            error: `No sessions found in ${timeRange} range`
        };
    }

    // Calculate comprehensive statistics
    const allAngles = filteredSessions.flatMap(s => 
        s.reps.map(r => r.angles.avg)
    );
    
    const totalReps = allAngles.length;
    const avgAngle = allAngles.reduce((a, b) => a + b, 0) / totalReps;
    const bestAngle = Math.min(...allAngles);
    const worstAngle = Math.max(...allAngles);
    
    // Session-level stats
    const sessionAvgs = filteredSessions.map(s => s.sessionStats.avgAngle);
    const avgPerSession = sessionAvgs.reduce((a, b) => a + b, 0) / sessionAvgs.length;
    
    // Improvement analysis
    const improvement = calculateImprovementRate(filteredSessions);
    
    // Consistency analysis
    const stdDev = calculateStdDev(allAngles);
    const overallConsistency = 1 - (stdDev / avgAngle);
    
    // Readiness assessment
    const readiness = assessReadinessForProgression({
        sessions: filteredSessions,
        currentTarget: currentLevel.personalTarget,
        personalBest: bestAngle,
        consistency: overallConsistency,
        consecutiveSuccesses: calculateConsecutiveSuccesses(filteredSessions)
    });

    return {
        userId,
        exerciseName,
        timeRange,
        reportDate: new Date().toISOString(),
        
        summary: {
            totalSessions: filteredSessions.length,
            totalReps,
            avgAngle: Math.round(avgAngle * 10) / 10,
            bestAngle: Math.round(bestAngle),
            worstAngle: Math.round(worstAngle),
            rangeOfMotion: Math.round(worstAngle - bestAngle),
            consistency: Math.round(overallConsistency * 100)
        },
        
        improvement: {
            ...improvement,
            firstSessionAvg: Math.round(sessionAvgs[0]),
            lastSessionAvg: Math.round(sessionAvgs[sessionAvgs.length - 1]),
            totalChange: Math.round(sessionAvgs[0] - sessionAvgs[sessionAvgs.length - 1])
        },
        
        currentStatus: {
            difficultyLevel: currentLevel.difficultyLevel || 'intermediate',
            personalTarget: currentLevel.personalTarget,
            readiness
        },
        
        milestones: identifyMilestones(filteredSessions, currentLevel.personalTarget),
        
        recommendations: generateRecommendations(
            improvement,
            overallConsistency,
            readiness,
            filteredSessions
        )
    };
}

/**
 * Calculate standard deviation
 */
function calculateStdDev(values) {
    const avg = values.reduce((a, b) => a + b, 0) / values.length;
    const squareDiffs = values.map(value => Math.pow(value - avg, 2));
    const avgSquareDiff = squareDiffs.reduce((a, b) => a + b, 0) / values.length;
    return Math.sqrt(avgSquareDiff);
}

/**
 * Calculate consecutive successful sessions
 */
function calculateConsecutiveSuccesses(sessions) {
    let count = 0;
    for (let i = sessions.length - 1; i >= 0; i--) {
        const session = sessions[i];
        // Success = completion rate > 0.8 and avg angle within 10% of target
        if (session.sessionStats.completionRate >= 0.8) {
            count++;
        } else {
            break;
        }
    }
    return count;
}

/**
 * Identify key milestones achieved
 */
function identifyMilestones(sessions, currentTarget) {
    const milestones = [];
    const allAngles = sessions.flatMap(s => s.reps.map(r => r.angles.avg));
    const bestAngle = Math.min(...allAngles);
    
    // Standard milestones
    const standardTargets = [120, 110, 100, 90, 80, 70];
    
    standardTargets.forEach(target => {
        if (bestAngle <= target) {
            milestones.push({
                type: 'target_achieved',
                value: target,
                date: sessions.find(s => 
                    s.reps.some(r => r.angles.avg <= target)
                )?.date
            });
        }
    });
    
    // Rep count milestones
    const totalReps = allAngles.length;
    const repMilestones = [10, 50, 100, 250, 500, 1000];
    const achievedReps = repMilestones.filter(m => totalReps >= m);
    if (achievedReps.length > 0) {
        milestones.push({
            type: 'total_reps',
            value: Math.max(...achievedReps),
            current: totalReps
        });
    }
    
    return milestones;
}

/**
 * Generate personalized recommendations
 */
function generateRecommendations(improvement, consistency, readiness, sessions) {
    const recommendations = [];
    
    // Based on improvement trend
    if (improvement.trend === 'improving') {
        recommendations.push({
            category: 'progression',
            priority: 'high',
            message: 'Great progress! Consider increasing difficulty.',
            action: 'Try deeper range of motion or more reps'
        });
    } else if (improvement.trend === 'declining') {
        recommendations.push({
            category: 'recovery',
            priority: 'high',
            message: 'Performance declining. Consider rest.',
            action: 'Take 2-3 days rest and reassess'
        });
    }
    
    // Based on consistency
    if (consistency < 0.6) {
        recommendations.push({
            category: 'consistency',
            priority: 'high',
            message: 'Focus on building consistency',
            action: 'Maintain current difficulty, practice form'
        });
    }
    
    // Based on readiness
    if (readiness.ready) {
        recommendations.push({
            category: 'level_up',
            priority: 'medium',
            message: 'Ready for next level!',
            action: 'Increase difficulty or try variations'
        });
    }
    
    // Based on session frequency
    const lastSession = new Date(sessions[sessions.length - 1].date);
    const daysSinceLastSession = (Date.now() - lastSession.getTime()) / (1000 * 60 * 60 * 24);
    
    if (daysSinceLastSession > 7) {
        recommendations.push({
            category: 'frequency',
            priority: 'medium',
            message: 'Maintain regular practice',
            action: 'Aim for 2-3 sessions per week'
        });
    }
    
    return recommendations;
}

// ============================================================================
// Comparative Analytics
// ============================================================================

/**
 * Compare user's progress against population averages
 * (Requires aggregated data from all users)
 * 
 * @param {Object} userData - Individual user data
 * @param {Object} populationData - Aggregated population statistics
 * @returns {Object} Comparative analysis
 */
export function compareToPopulation(userData, populationData) {
    const { progressMetrics = {} } = userData;
    const { averageImprovement, averageConsistency, percentiles } = populationData;
    
    const userImprovement = progressMetrics.improvementRate || 0;
    const userConsistency = progressMetrics.averageConsistency || 0;
    
    // Calculate percentile rank
    let percentileRank = 50; // Default to median
    if (percentiles) {
        percentileRank = Object.entries(percentiles)
            .sort(([a], [b]) => Number(b) - Number(a))
            .find(([_, value]) => userImprovement >= value)?.[0] || 50;
    }
    
    return {
        improvementComparison: {
            user: userImprovement,
            average: averageImprovement,
            difference: userImprovement - averageImprovement,
            percentile: percentileRank
        },
        consistencyComparison: {
            user: userConsistency,
            average: averageConsistency,
            difference: userConsistency - averageConsistency
        },
        message: getComparisonMessage(userImprovement, averageImprovement, percentileRank)
    };
}

function getComparisonMessage(userRate, avgRate, percentile) {
    if (percentile >= 75) {
        return `Outstanding! You're in the top ${100 - percentile}% of users.`;
    } else if (percentile >= 50) {
        return `Good progress! Above average performance.`;
    } else {
        return `Keep going! Consistency is key to improvement.`;
    }
}

// Export all functions
export default {
    calculateImprovementRate,
    predictNextTarget,
    assessReadinessForProgression,
    generateProgressReport,
    compareToPopulation
};
