/**
 * Reward System for Pose2Play Rehabilitation App
 * 
 * Gamification system designed for physical therapy patients (ages 14-80)
 * Focuses on positive reinforcement, consistency, and personal progress
 * 
 * Uses Recovery Points (RP) instead of XP to maintain medical context
 */

// ============================================================================
// Configuration
// ============================================================================

export const rewardConfig = {
    // Recovery Points (RP) award amounts
    rpAwards: {
        repCompleted: 10,           // Base RP for completing any rep
        goodForm: 5,                // Bonus for form within 10° of target
        perfectForm: 10,            // Bonus for hitting target angle
        sessionComplete: 50,        // Bonus for finishing full session
        dailyGoalMet: 100,         // Complete daily goal
        streakBonus: 20,           // Per day of active streak
        weeklyGoalMet: 150,        // Complete 3+ sessions in a week
        personalBest: 25,          // Beat your own record
        difficultyIncrease: 200,   // Adaptive system levels you up
        consistencyBonus: 30       // Maintain 80%+ form consistency in session
    },

    // Level progression (Recovery Levels)
    levels: [
        { level: 1, name: "Building Foundation", minRP: 0, maxRP: 200 },
        { level: 2, name: "Building Foundation", minRP: 200, maxRP: 400 },
        { level: 3, name: "Building Foundation", minRP: 400, maxRP: 700 },
        { level: 4, name: "Gaining Strength", minRP: 700, maxRP: 1100 },
        { level: 5, name: "Gaining Strength", minRP: 1100, maxRP: 1600 },
        { level: 6, name: "Gaining Strength", minRP: 1600, maxRP: 2200 },
        { level: 7, name: "Rebuilding Confidence", minRP: 2200, maxRP: 2900 },
        { level: 8, name: "Rebuilding Confidence", minRP: 2900, maxRP: 3700 },
        { level: 9, name: "Rebuilding Confidence", minRP: 3700, maxRP: 4600 },
        { level: 10, name: "Recovery Champion", minRP: 4600, maxRP: 5600 },
        { level: 11, name: "Recovery Champion", minRP: 5600, maxRP: 6800 },
        { level: 12, name: "Recovery Champion", minRP: 6800, maxRP: 8200 },
        { level: 13, name: "Recovery Master", minRP: 8200, maxRP: 10000 },
        { level: 14, name: "Recovery Master", minRP: 10000, maxRP: 12000 },
        { level: 15, name: "Recovery Master", minRP: 12000, maxRP: 15000 },
        { level: 16, name: "Rehabilitation Expert", minRP: 15000, maxRP: 18500 },
        { level: 17, name: "Rehabilitation Expert", minRP: 18500, maxRP: 22500 },
        { level: 18, name: "Rehabilitation Expert", minRP: 22500, maxRP: 27000 },
        { level: 19, name: "Movement Maestro", minRP: 27000, maxRP: 32000 },
        { level: 20, name: "Movement Maestro", minRP: 32000, maxRP: Infinity }
    ],

    // Daily goal configuration
    dailyGoal: {
        minReps: 20,           // Minimum reps to count as daily goal
        minExercises: 1,       // Minimum exercises to complete
        minSessionDuration: 300 // Minimum 5 minutes
    },

    // Streak configuration
    streaks: {
        milestones: [3, 7, 14, 30, 60, 90], // Days that trigger special rewards
        gracePeriod: 36 // Hours allowed to maintain streak (1.5 days for flexibility)
    }
};

// ============================================================================
// Recovery Points (RP) Calculation
// ============================================================================

/**
 * Calculate RP earned for a single rep
 * 
 * @param {Object} repData - Rep performance data from exercise tracker
 * @param {number} targetAngle - Target angle for this exercise
 * @returns {Object} RP breakdown and total
 */
export function calculateRepRP(repData, targetAngle) {
    const { angles, success } = repData;
    const avgAngle = angles.avg;
    
    let rpBreakdown = {
        base: 0,
        formBonus: 0,
        total: 0,
        reason: []
    };

    // Base RP for completing the rep
    rpBreakdown.base = rewardConfig.rpAwards.repCompleted;
    rpBreakdown.reason.push(`Completed rep: +${rpBreakdown.base} RP`);

    // Form quality bonus
    const angleDifference = Math.abs(avgAngle - targetAngle);
    
    if (angleDifference <= 2) {
        // Perfect form - within 2° of target
        rpBreakdown.formBonus = rewardConfig.rpAwards.perfectForm;
        rpBreakdown.reason.push(`Perfect form! +${rpBreakdown.formBonus} RP`);
    } else if (angleDifference <= 10) {
        // Good form - within 10° of target
        rpBreakdown.formBonus = rewardConfig.rpAwards.goodForm;
        rpBreakdown.reason.push(`Good form! +${rpBreakdown.formBonus} RP`);
    }

    rpBreakdown.total = rpBreakdown.base + rpBreakdown.formBonus;

    return rpBreakdown;
}

/**
 * Calculate RP for completing a session
 * 
 * @param {Object} sessionData - Session summary from adaptive learning
 * @param {Object} userStats - User's current stats (streak, goals, etc.)
 * @returns {Object} Session RP breakdown
 */
export function calculateSessionRP(sessionData, userStats = {}) {
    const { reps = [], sessionStats = {} } = sessionData;
    const { consistencyScore = 0, completionRate = 0 } = sessionStats;
    
    let rpBreakdown = {
        repsTotal: 0,
        sessionBonus: 0,
        consistencyBonus: 0,
        streakBonus: 0,
        personalBestBonus: 0,
        total: 0,
        achievements: []
    };

    // Sum up all rep RP
    reps.forEach(rep => {
        const repRP = calculateRepRP(rep, rep.targetAngle);
        rpBreakdown.repsTotal += repRP.total;
    });

    // Session completion bonus
    if (completionRate >= 0.8) {
        rpBreakdown.sessionBonus = rewardConfig.rpAwards.sessionComplete;
        rpBreakdown.achievements.push(`Session completed! +${rpBreakdown.sessionBonus} RP`);
    }

    // Consistency bonus (maintaining good form throughout)
    if (consistencyScore >= 0.8) {
        rpBreakdown.consistencyBonus = rewardConfig.rpAwards.consistencyBonus;
        rpBreakdown.achievements.push(`Great consistency! +${rpBreakdown.consistencyBonus} RP`);
    }

    // Streak bonus
    if (userStats.currentStreak > 0) {
        const streakDays = userStats.currentStreak;
        rpBreakdown.streakBonus = rewardConfig.rpAwards.streakBonus * streakDays;
        rpBreakdown.achievements.push(`${streakDays} day streak! +${rpBreakdown.streakBonus} RP`);
    }

    // Personal best bonus
    if (userStats.isPersonalBest) {
        rpBreakdown.personalBestBonus = rewardConfig.rpAwards.personalBest;
        rpBreakdown.achievements.push(`New personal best! +${rpBreakdown.personalBestBonus} RP`);
    }

    rpBreakdown.total = 
        rpBreakdown.repsTotal + 
        rpBreakdown.sessionBonus + 
        rpBreakdown.consistencyBonus + 
        rpBreakdown.streakBonus + 
        rpBreakdown.personalBestBonus;

    return rpBreakdown;
}

// ============================================================================
// Level Progression
// ============================================================================

/**
 * Get user's current level based on total RP
 * 
 * @param {number} totalRP - User's total accumulated RP
 * @returns {Object} Level information
 */
export function getUserLevel(totalRP) {
    let currentLevel = rewardConfig.levels[0];
    
    for (const level of rewardConfig.levels) {
        if (totalRP >= level.minRP && totalRP < level.maxRP) {
            currentLevel = level;
            break;
        }
    }

    const progressToNext = totalRP - currentLevel.minRP;
    const rpNeededForNext = currentLevel.maxRP - currentLevel.minRP;
    const progressPercentage = Math.min(100, Math.round((progressToNext / rpNeededForNext) * 100));

    return {
        level: currentLevel.level,
        name: currentLevel.name,
        currentRP: totalRP,
        minRP: currentLevel.minRP,
        maxRP: currentLevel.maxRP,
        rpToNextLevel: currentLevel.maxRP - totalRP,
        progressPercentage,
        isMaxLevel: currentLevel.maxRP === Infinity
    };
}

/**
 * Check if user leveled up after earning RP
 * 
 * @param {number} oldRP - RP before earning
 * @param {number} newRP - RP after earning
 * @returns {Object|null} Level up info or null if no level up
 */
export function checkLevelUp(oldRP, newRP) {
    const oldLevel = getUserLevel(oldRP);
    const newLevel = getUserLevel(newRP);

    if (newLevel.level > oldLevel.level) {
        return {
            leveledUp: true,
            oldLevel: oldLevel.level,
            newLevel: newLevel.level,
            newLevelName: newLevel.name,
            bonusRP: rewardConfig.rpAwards.difficultyIncrease,
            message: `🎉 Level Up! You've reached ${newLevel.name} (Level ${newLevel.level})!`
        };
    }

    return null;
}

// ============================================================================
// Streak Tracking
// ============================================================================

/**
 * Update user's activity streak
 * 
 * @param {Object} userRewards - Current user reward data
 * @param {Date} lastActivityDate - Last time user completed a session
 * @returns {Object} Updated streak information
 */
export function updateStreak(userRewards, lastActivityDate = null) {
    const now = new Date();
    const { streakDays = 0, lastActivity = null } = userRewards;

    if (!lastActivityDate && !lastActivity) {
        // First activity ever
        return {
            streakDays: 1,
            lastActivity: now.toISOString(),
            streakStatus: 'started',
            message: '🔥 Streak started! Come back tomorrow to keep it going!',
            milestoneReached: false
        };
    }

    const lastDate = new Date(lastActivityDate || lastActivity);
    const hoursSinceLastActivity = (now - lastDate) / (1000 * 60 * 60);

    let newStreak = streakDays;
    let streakStatus = 'maintained';
    let message = '';
    let milestoneReached = false;
    let milestoneBonus = 0;

    if (hoursSinceLastActivity <= 24) {
        // Same day - no change
        streakStatus = 'same_day';
        message = 'Great work today! Your streak continues.';
    } else if (hoursSinceLastActivity <= rewardConfig.streaks.gracePeriod) {
        // Within grace period - increment streak
        newStreak += 1;
        streakStatus = 'increased';
        message = `🔥 ${newStreak} day streak! Keep it up!`;

        // Check for milestone
        if (rewardConfig.streaks.milestones.includes(newStreak)) {
            milestoneReached = true;
            milestoneBonus = newStreak * 10; // Milestone bonus scales with streak length
            message = `🏆 ${newStreak} DAY STREAK MILESTONE! +${milestoneBonus} bonus RP!`;
        }
    } else {
        // Streak broken
        newStreak = 1;
        streakStatus = 'broken';
        message = `Streak reset. But that's okay - you're back! New streak: 1 day.`;
    }

    return {
        streakDays: newStreak,
        lastActivity: now.toISOString(),
        streakStatus,
        message,
        milestoneReached,
        milestoneBonus
    };
}

// ============================================================================
// Daily/Weekly Goals
// ============================================================================

/**
 * Check if daily goal is met
 * 
 * @param {Object} todayStats - User's stats for today
 * @returns {Object} Goal status
 */
export function checkDailyGoal(todayStats) {
    const { totalReps = 0, exercisesCompleted = 0, totalDuration = 0 } = todayStats;
    
    const repsGoalMet = totalReps >= rewardConfig.dailyGoal.minReps;
    const exerciseGoalMet = exercisesCompleted >= rewardConfig.dailyGoal.minExercises;
    const durationGoalMet = totalDuration >= rewardConfig.dailyGoal.minSessionDuration;

    const goalMet = repsGoalMet && exerciseGoalMet && durationGoalMet;

    return {
        goalMet,
        repsGoalMet,
        exerciseGoalMet,
        durationGoalMet,
        repsProgress: Math.round((totalReps / rewardConfig.dailyGoal.minReps) * 100),
        bonusRP: goalMet ? rewardConfig.rpAwards.dailyGoalMet : 0,
        message: goalMet 
            ? `🎯 Daily goal achieved! +${rewardConfig.rpAwards.dailyGoalMet} RP` 
            : `Keep going! ${totalReps}/${rewardConfig.dailyGoal.minReps} reps completed.`
    };
}

/**
 * Check if weekly goal is met (3+ sessions)
 * 
 * @param {Array} weekSessions - Sessions from the past 7 days
 * @returns {Object} Weekly goal status
 */
export function checkWeeklyGoal(weekSessions) {
    const sessionsThisWeek = weekSessions.length;
    const goalMet = sessionsThisWeek >= 3;

    return {
        goalMet,
        sessionsCompleted: sessionsThisWeek,
        sessionsRequired: 3,
        bonusRP: goalMet ? rewardConfig.rpAwards.weeklyGoalMet : 0,
        message: goalMet 
            ? `🌟 Weekly goal achieved! ${sessionsThisWeek} sessions this week! +${rewardConfig.rpAwards.weeklyGoalMet} RP`
            : `${sessionsThisWeek}/3 sessions this week. Keep it up!`
    };
}

// ============================================================================
// Main Reward Processing
// ============================================================================

/**
 * Process all rewards for a completed session
 * This is the main function to call when a user finishes exercising
 * 
 * @param {string} userId - User identifier
 * @param {Object} sessionData - Session data from exercise tracker
 * @param {Object} currentUserRewards - Current user reward data from database
 * @param {Object} recentActivity - User's recent activity stats
 * @returns {Object} Complete reward summary
 */
export function processSessionRewards(userId, sessionData, currentUserRewards, recentActivity = {}) {
    const {
        totalRP = 0,
        streakDays = 0,
        lastActivity = null,
        level = 1
    } = currentUserRewards;

    // Calculate session RP
    const streakInfo = updateStreak({ streakDays, lastActivity });
    const userStats = {
        currentStreak: streakInfo.streakDays,
        isPersonalBest: sessionData.isPersonalBest || false
    };

    const sessionRP = calculateSessionRP(sessionData, userStats);

    // Add streak milestone bonus
    if (streakInfo.milestoneReached) {
        sessionRP.total += streakInfo.milestoneBonus;
        sessionRP.achievements.push(streakInfo.message);
    }

    // Calculate new total RP
    const newTotalRP = totalRP + sessionRP.total;

    // Check for level up
    const levelUp = checkLevelUp(totalRP, newTotalRP);
    if (levelUp) {
        sessionRP.total += levelUp.bonusRP;
        sessionRP.achievements.push(levelUp.message);
    }

    // Check daily goal
    const dailyGoal = checkDailyGoal(recentActivity.today || {});
    if (dailyGoal.goalMet && !recentActivity.dailyGoalMetToday) {
        sessionRP.total += dailyGoal.bonusRP;
        sessionRP.achievements.push(dailyGoal.message);
    }

    // Check weekly goal
    const weeklyGoal = checkWeeklyGoal(recentActivity.thisWeek || []);
    if (weeklyGoal.goalMet && !recentActivity.weeklyGoalMetThisWeek) {
        sessionRP.total += weeklyGoal.bonusRP;
        sessionRP.achievements.push(weeklyGoal.message);
    }

    // Get updated level info
    const levelInfo = getUserLevel(newTotalRP);

    return {
        userId,
        sessionRP: sessionRP.total,
        rpBreakdown: sessionRP,
        oldTotalRP: totalRP,
        newTotalRP,
        rpEarned: sessionRP.total,
        levelInfo,
        leveledUp: levelUp !== null,
        levelUpInfo: levelUp,
        streakInfo,
        dailyGoalInfo: dailyGoal,
        weeklyGoalInfo: weeklyGoal,
        achievements: sessionRP.achievements,
        summary: {
            reps: sessionData.reps?.length || 0,
            rpPerRep: Math.round(sessionRP.repsTotal / (sessionData.reps?.length || 1)),
            totalRP: newTotalRP,
            level: levelInfo.level,
            streak: streakInfo.streakDays
        }
    };
}

// ============================================================================
// Utility Functions
// ============================================================================

/**
 * Get motivational message based on RP earned
 * 
 * @param {number} rpEarned - RP earned in session
 * @param {number} userAge - User's age (for age-appropriate messaging)
 * @returns {string} Motivational message
 */
export function getMotivationalMessage(rpEarned, userAge = 40) {
    const messages = {
        young: { // 14-30
            low: ["Nice work! Every rep counts! 💪", "You're building momentum!", "Keep grinding! 🔥"],
            medium: ["Crushing it! Keep it up! 🚀", "That's what I'm talking about! ⚡", "On fire today! 🔥"],
            high: ["LEGENDARY session! 🏆", "You're unstoppable! 🌟", "That was INCREDIBLE! 🎯"]
        },
        middle: { // 30-60
            low: ["Great work today!", "You showed up - that's what matters!", "Steady progress! Keep going!"],
            medium: ["Excellent session! You're making real progress!", "Really impressive work today!", "You're getting stronger!"],
            high: ["Outstanding! What a session!", "Phenomenal effort! You should be proud!", "Incredible dedication!"]
        },
        senior: { // 60+
            low: ["Well done! Your dedication is inspiring.", "Great effort today!", "You're doing wonderfully!"],
            medium: ["Excellent work! Your consistency is paying off!", "Wonderful progress! Keep it up!", "Very impressive!"],
            high: ["Remarkable! What an achievement!", "Exceptional work today!", "Your progress is truly inspiring!"]
        }
    };

    // Determine age group
    let ageGroup = 'middle';
    if (userAge < 30) ageGroup = 'young';
    else if (userAge >= 60) ageGroup = 'senior';

    // Determine performance level
    let perfLevel = 'low';
    if (rpEarned >= 500) perfLevel = 'high';
    else if (rpEarned >= 250) perfLevel = 'medium';

    const options = messages[ageGroup][perfLevel];
    return options[Math.floor(Math.random() * options.length)];
}

/**
 * Format RP for display
 * 
 * @param {number} rp - Recovery Points
 * @returns {string} Formatted string
 */
export function formatRP(rp) {
    if (rp >= 1000) {
        return `${(rp / 1000).toFixed(1)}k RP`;
    }
    return `${rp} RP`;
}

// Export default object with all functions
export default {
    rewardConfig,
    calculateRepRP,
    calculateSessionRP,
    getUserLevel,
    checkLevelUp,
    updateStreak,
    checkDailyGoal,
    checkWeeklyGoal,
    processSessionRewards,
    getMotivationalMessage,
    formatRP
};
