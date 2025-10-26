/**
 * Achievement System for Pose2Play
 * 
 * Badge and milestone tracking for rehabilitation motivation
 * Age-appropriate achievements for patients 14-80 years old
 */

// ============================================================================
// Achievement Definitions
// ============================================================================

export const achievements = {
    // ========== Getting Started Achievements ==========
    first_step: {
        id: 'first_step',
        name: 'First Step',
        description: 'Complete your first exercise session',
        icon: '🏁',
        category: 'milestone',
        rpReward: 50,
        requirement: {
            type: 'sessions_completed',
            value: 1
        },
        ageAppropriate: 'all'
    },

    beginner_badge: {
        id: 'beginner_badge',
        name: 'Beginner Badge',
        description: 'Complete 5 exercise sessions',
        icon: '🌱',
        category: 'milestone',
        rpReward: 100,
        requirement: {
            type: 'sessions_completed',
            value: 5
        },
        ageAppropriate: 'all'
    },

    // ========== Rep Milestones ==========
    century_club: {
        id: 'century_club',
        name: 'Century Club',
        description: 'Complete 100 total reps',
        icon: '💯',
        category: 'milestone',
        rpReward: 150,
        requirement: {
            type: 'total_reps',
            value: 100
        },
        ageAppropriate: 'all'
    },

    rep_warrior_500: {
        id: 'rep_warrior_500',
        name: 'Rep Warrior',
        description: 'Complete 500 total reps',
        icon: '⚔️',
        category: 'milestone',
        rpReward: 300,
        requirement: {
            type: 'total_reps',
            value: 500
        },
        ageAppropriate: 'young,middle'
    },

    thousand_strong: {
        id: 'thousand_strong',
        name: 'Thousand Strong',
        description: 'Complete 1000 total reps',
        icon: '🏋️',
        category: 'milestone',
        rpReward: 500,
        requirement: {
            type: 'total_reps',
            value: 1000
        },
        ageAppropriate: 'young,middle'
    },

    dedication_500: {
        id: 'dedication_500',
        name: 'Dedication',
        description: 'Complete 500 total reps',
        icon: '🌟',
        category: 'milestone',
        rpReward: 300,
        requirement: {
            type: 'total_reps',
            value: 500
        },
        ageAppropriate: 'senior'
    },

    // ========== Form & Quality Achievements ==========
    bullseye: {
        id: 'bullseye',
        name: 'Bullseye',
        description: 'Achieve 10 perfect form reps (within 2° of target)',
        icon: '🎯',
        category: 'form',
        rpReward: 200,
        requirement: {
            type: 'perfect_form_reps',
            value: 10
        },
        ageAppropriate: 'all'
    },

    form_master: {
        id: 'form_master',
        name: 'Form Master',
        description: 'Achieve 50 perfect form reps',
        icon: '🎖️',
        category: 'form',
        rpReward: 400,
        requirement: {
            type: 'perfect_form_reps',
            value: 50
        },
        ageAppropriate: 'all'
    },

    consistency_king: {
        id: 'consistency_king',
        name: 'Consistency Champion',
        description: 'Complete a session with 90%+ form consistency',
        icon: '💎',
        category: 'form',
        rpReward: 250,
        requirement: {
            type: 'session_consistency',
            value: 0.9
        },
        ageAppropriate: 'all'
    },

    // ========== Streak Achievements ==========
    three_day_flame: {
        id: 'three_day_flame',
        name: '3 Day Flame',
        description: 'Maintain a 3 day streak',
        icon: '🔥',
        category: 'streak',
        rpReward: 100,
        requirement: {
            type: 'streak_days',
            value: 3
        },
        ageAppropriate: 'all'
    },

    week_warrior: {
        id: 'week_warrior',
        name: 'Week Warrior',
        description: 'Maintain a 7 day streak',
        icon: '⚡',
        category: 'streak',
        rpReward: 250,
        requirement: {
            type: 'streak_days',
            value: 7
        },
        ageAppropriate: 'young,middle'
    },

    dedication_week: {
        id: 'dedication_week',
        name: 'Weekly Dedication',
        description: 'Maintain a 7 day streak',
        icon: '🌟',
        category: 'streak',
        rpReward: 250,
        requirement: {
            type: 'streak_days',
            value: 7
        },
        ageAppropriate: 'senior'
    },

    fortnight_champion: {
        id: 'fortnight_champion',
        name: 'Fortnight Champion',
        description: 'Maintain a 14 day streak',
        icon: '🏅',
        category: 'streak',
        rpReward: 500,
        requirement: {
            type: 'streak_days',
            value: 14
        },
        ageAppropriate: 'all'
    },

    month_master: {
        id: 'month_master',
        name: 'Month Master',
        description: 'Maintain a 30 day streak',
        icon: '🏆',
        category: 'streak',
        rpReward: 1000,
        requirement: {
            type: 'streak_days',
            value: 30
        },
        ageAppropriate: 'all'
    },

    unstoppable: {
        id: 'unstoppable',
        name: 'Unstoppable',
        description: 'Maintain a 60 day streak',
        icon: '🌟',
        category: 'streak',
        rpReward: 2000,
        requirement: {
            type: 'streak_days',
            value: 60
        },
        ageAppropriate: 'all'
    },

    // ========== Progress Achievements ==========
    progress_rocket: {
        id: 'progress_rocket',
        name: 'Progress Rocket',
        description: 'Increase difficulty level in adaptive training',
        icon: '🚀',
        category: 'progression',
        rpReward: 300,
        requirement: {
            type: 'difficulty_increase',
            value: 1
        },
        ageAppropriate: 'young,middle'
    },

    steady_climber: {
        id: 'steady_climber',
        name: 'Steady Climber',
        description: 'Increase difficulty level in adaptive training',
        icon: '📈',
        category: 'progression',
        rpReward: 300,
        requirement: {
            type: 'difficulty_increase',
            value: 1
        },
        ageAppropriate: 'senior'
    },

    personal_best: {
        id: 'personal_best',
        name: 'Personal Best',
        description: 'Beat your previous best angle',
        icon: '⭐',
        category: 'progression',
        rpReward: 100,
        requirement: {
            type: 'personal_best_count',
            value: 1
        },
        ageAppropriate: 'all'
    },

    overachiever: {
        id: 'overachiever',
        name: 'Overachiever',
        description: 'Beat your personal best 10 times',
        icon: '🌟',
        category: 'progression',
        rpReward: 400,
        requirement: {
            type: 'personal_best_count',
            value: 10
        },
        ageAppropriate: 'all'
    },

    // ========== Session-based Achievements ==========
    power_session: {
        id: 'power_session',
        name: 'Power Session',
        description: 'Complete 50+ reps in a single session',
        icon: '💪',
        category: 'session',
        rpReward: 200,
        requirement: {
            type: 'reps_in_session',
            value: 50
        },
        ageAppropriate: 'young,middle'
    },

    endurance_master: {
        id: 'endurance_master',
        name: 'Endurance Master',
        description: 'Complete a 20-minute session',
        icon: '⏱️',
        category: 'session',
        rpReward: 250,
        requirement: {
            type: 'session_duration',
            value: 1200 // 20 minutes in seconds
        },
        ageAppropriate: 'all'
    },

    multi_exercise: {
        id: 'multi_exercise',
        name: 'Multi-Exercise Champion',
        description: 'Complete 3 different exercises in one session',
        icon: '🎪',
        category: 'session',
        rpReward: 300,
        requirement: {
            type: 'exercises_in_session',
            value: 3
        },
        ageAppropriate: 'all'
    },

    // ========== Level Achievements ==========
    level_5: {
        id: 'level_5',
        name: 'Gaining Strength',
        description: 'Reach Recovery Level 5',
        icon: '🌿',
        category: 'level',
        rpReward: 500,
        requirement: {
            type: 'level_reached',
            value: 5
        },
        ageAppropriate: 'all'
    },

    level_10: {
        id: 'level_10',
        name: 'Recovery Champion',
        description: 'Reach Recovery Level 10',
        icon: '🏆',
        category: 'level',
        rpReward: 1000,
        requirement: {
            type: 'level_reached',
            value: 10
        },
        ageAppropriate: 'all'
    },

    level_15: {
        id: 'level_15',
        name: 'Recovery Master',
        description: 'Reach Recovery Level 15',
        icon: '👑',
        category: 'level',
        rpReward: 2000,
        requirement: {
            type: 'level_reached',
            value: 15
        },
        ageAppropriate: 'all'
    },

    // ========== Consistency Achievements ==========
    weekly_routine: {
        id: 'weekly_routine',
        name: 'Weekly Routine',
        description: 'Complete 3+ sessions in a week',
        icon: '📅',
        category: 'consistency',
        rpReward: 200,
        requirement: {
            type: 'weekly_sessions',
            value: 3
        },
        ageAppropriate: 'all'
    },

    monthly_commitment: {
        id: 'monthly_commitment',
        name: 'Monthly Commitment',
        description: 'Complete 12+ sessions in a month',
        icon: '🗓️',
        category: 'consistency',
        rpReward: 750,
        requirement: {
            type: 'monthly_sessions',
            value: 12
        },
        ageAppropriate: 'all'
    }
};

// ============================================================================
// Achievement Checking Functions
// ============================================================================

/**
 * Check if user has unlocked a specific achievement
 * 
 * @param {Object} achievement - Achievement definition
 * @param {Object} userStats - User's current statistics
 * @returns {boolean} Whether achievement is unlocked
 */
export function checkAchievement(achievement, userStats) {
    const { requirement } = achievement;
    const { type, value } = requirement;

    switch (type) {
        case 'sessions_completed':
            return userStats.totalSessions >= value;
        
        case 'total_reps':
            return userStats.totalReps >= value;
        
        case 'perfect_form_reps':
            return (userStats.perfectFormReps || 0) >= value;
        
        case 'session_consistency':
            return (userStats.lastSessionConsistency || 0) >= value;
        
        case 'streak_days':
            return (userStats.currentStreak || 0) >= value;
        
        case 'difficulty_increase':
            return (userStats.difficultyIncreases || 0) >= value;
        
        case 'personal_best_count':
            return (userStats.personalBestCount || 0) >= value;
        
        case 'reps_in_session':
            return (userStats.lastSessionReps || 0) >= value;
        
        case 'session_duration':
            return (userStats.lastSessionDuration || 0) >= value;
        
        case 'exercises_in_session':
            return (userStats.lastSessionExercises || 0) >= value;
        
        case 'level_reached':
            return (userStats.currentLevel || 1) >= value;
        
        case 'weekly_sessions':
            return (userStats.thisWeekSessions || 0) >= value;
        
        case 'monthly_sessions':
            return (userStats.thisMonthSessions || 0) >= value;
        
        default:
            return false;
    }
}

/**
 * Get age-appropriate achievements for a user
 * 
 * @param {number} userAge - User's age
 * @returns {Array} Filtered achievements appropriate for age
 */
export function getAgeAppropriateAchievements(userAge) {
    let ageGroup = 'middle';
    if (userAge < 30) ageGroup = 'young';
    else if (userAge >= 60) ageGroup = 'senior';

    return Object.values(achievements).filter(achievement => {
        const appropriate = achievement.ageAppropriate;
        return appropriate === 'all' || appropriate.includes(ageGroup);
    });
}

/**
 * Check all achievements and return newly unlocked ones
 * 
 * @param {Object} userStats - User's current statistics
 * @param {Array} unlockedAchievements - Array of already unlocked achievement IDs
 * @param {number} userAge - User's age for age-appropriate filtering
 * @returns {Array} Newly unlocked achievements
 */
export function checkNewAchievements(userStats, unlockedAchievements = [], userAge = 40) {
    const ageAppropriate = getAgeAppropriateAchievements(userAge);
    const newlyUnlocked = [];

    ageAppropriate.forEach(achievement => {
        // Skip if already unlocked
        if (unlockedAchievements.includes(achievement.id)) {
            return;
        }

        // Check if requirements are met
        if (checkAchievement(achievement, userStats)) {
            newlyUnlocked.push({
                ...achievement,
                unlockedAt: new Date().toISOString()
            });
        }
    });

    return newlyUnlocked;
}

/**
 * Get achievement progress for display
 * 
 * @param {Object} achievement - Achievement definition
 * @param {Object} userStats - User's current statistics
 * @returns {Object} Progress information
 */
export function getAchievementProgress(achievement, userStats) {
    const { requirement } = achievement;
    const { type, value } = requirement;

    let current = 0;
    let percentage = 0;

    switch (type) {
        case 'sessions_completed':
            current = userStats.totalSessions || 0;
            break;
        case 'total_reps':
            current = userStats.totalReps || 0;
            break;
        case 'perfect_form_reps':
            current = userStats.perfectFormReps || 0;
            break;
        case 'streak_days':
            current = userStats.currentStreak || 0;
            break;
        case 'difficulty_increase':
            current = userStats.difficultyIncreases || 0;
            break;
        case 'personal_best_count':
            current = userStats.personalBestCount || 0;
            break;
        case 'level_reached':
            current = userStats.currentLevel || 1;
            break;
        case 'weekly_sessions':
            current = userStats.thisWeekSessions || 0;
            break;
        case 'monthly_sessions':
            current = userStats.thisMonthSessions || 0;
            break;
        default:
            current = 0;
    }

    percentage = Math.min(100, Math.round((current / value) * 100));

    return {
        current,
        required: value,
        percentage,
        completed: current >= value,
        remaining: Math.max(0, value - current)
    };
}

/**
 * Get achievements by category
 * 
 * @param {string} category - Category name ('milestone', 'streak', 'form', etc.)
 * @param {number} userAge - User's age for filtering
 * @returns {Array} Achievements in category
 */
export function getAchievementsByCategory(category, userAge = 40) {
    const ageAppropriate = getAgeAppropriateAchievements(userAge);
    return ageAppropriate.filter(achievement => achievement.category === category);
}

/**
 * Get total RP available from all achievements
 * 
 * @param {number} userAge - User's age
 * @returns {number} Total possible RP from achievements
 */
export function getTotalAchievementRP(userAge = 40) {
    const ageAppropriate = getAgeAppropriateAchievements(userAge);
    return ageAppropriate.reduce((sum, achievement) => sum + achievement.rpReward, 0);
}

/**
 * Get user's achievement summary
 * 
 * @param {Array} unlockedAchievements - User's unlocked achievement IDs
 * @param {number} userAge - User's age
 * @returns {Object} Summary statistics
 */
export function getAchievementSummary(unlockedAchievements = [], userAge = 40) {
    const ageAppropriate = getAgeAppropriateAchievements(userAge);
    const total = ageAppropriate.length;
    const unlocked = unlockedAchievements.length;
    
    const rpEarned = ageAppropriate
        .filter(a => unlockedAchievements.includes(a.id))
        .reduce((sum, a) => sum + a.rpReward, 0);
    
    const totalPossibleRP = getTotalAchievementRP(userAge);

    // Category breakdown
    const categories = ['milestone', 'streak', 'form', 'progression', 'session', 'level', 'consistency'];
    const categoryProgress = {};
    
    categories.forEach(category => {
        const categoryAchievements = getAchievementsByCategory(category, userAge);
        const categoryUnlocked = categoryAchievements.filter(a => 
            unlockedAchievements.includes(a.id)
        ).length;
        
        categoryProgress[category] = {
            total: categoryAchievements.length,
            unlocked: categoryUnlocked,
            percentage: categoryAchievements.length > 0 
                ? Math.round((categoryUnlocked / categoryAchievements.length) * 100)
                : 0
        };
    });

    return {
        totalAchievements: total,
        unlockedAchievements: unlocked,
        completionPercentage: Math.round((unlocked / total) * 100),
        rpEarned,
        totalPossibleRP,
        categoryProgress
    };
}

// ============================================================================
// Utility Functions
// ============================================================================

/**
 * Get next achievable achievements (closest to unlocking)
 * 
 * @param {Object} userStats - User's current statistics
 * @param {Array} unlockedAchievements - Already unlocked achievement IDs
 * @param {number} userAge - User's age
 * @param {number} limit - Max achievements to return
 * @returns {Array} Next achievements to work towards
 */
export function getNextAchievements(userStats, unlockedAchievements = [], userAge = 40, limit = 3) {
    const ageAppropriate = getAgeAppropriateAchievements(userAge);
    
    const locked = ageAppropriate.filter(a => !unlockedAchievements.includes(a.id));
    
    const withProgress = locked.map(achievement => ({
        ...achievement,
        progress: getAchievementProgress(achievement, userStats)
    }));

    // Sort by completion percentage (closest to completion first)
    withProgress.sort((a, b) => b.progress.percentage - a.progress.percentage);

    return withProgress.slice(0, limit);
}

/**
 * Format achievement notification message
 * 
 * @param {Object} achievement - Achievement that was unlocked
 * @returns {string} Formatted message
 */
export function formatAchievementNotification(achievement) {
    return `${achievement.icon} Achievement Unlocked: ${achievement.name}! +${achievement.rpReward} RP`;
}

// Export all functions
export default {
    achievements,
    checkAchievement,
    getAgeAppropriateAchievements,
    checkNewAchievements,
    getAchievementProgress,
    getAchievementsByCategory,
    getTotalAchievementRP,
    getAchievementSummary,
    getNextAchievements,
    formatAchievementNotification
};
