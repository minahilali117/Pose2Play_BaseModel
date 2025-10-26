/**
 * Motivation Engine for Pose2Play
 * 
 * Provides age-appropriate, context-aware encouragement messages
 * for rehabilitation patients (ages 14-80)
 */

// ============================================================================
// Encouragement Messages by Context
// ============================================================================

const motivationMessages = {
    // ========== Session Start Messages ==========
    sessionStart: {
        young: [
            "Let's crush this workout! 💪",
            "Time to level up your recovery! 🚀",
            "You got this! Let's go! 🔥",
            "Ready to smash your goals? Let's do it!",
            "Game on! Show that knee who's boss! 🎯"
        ],
        middle: [
            "Ready to make progress today?",
            "Let's build on yesterday's success!",
            "Time to take another step forward!",
            "Your recovery journey continues!",
            "Let's focus on quality movement today."
        ],
        senior: [
            "Welcome! Let's work on your recovery today.",
            "Ready to continue your progress?",
            "Time for today's exercises.",
            "Let's take this one step at a time.",
            "Great to see you back!"
        ]
    },

    // ========== During Exercise (Good Form) ==========
    goodForm: {
        young: [
            "Perfect! Keep it up! 🎯",
            "That's the way! Nailed it! ⚡",
            "Excellent form! You're crushing it!",
            "On point! Keep going! 🔥",
            "Yes! That's how it's done! 💪"
        ],
        middle: [
            "Great form! You're doing well!",
            "Excellent! Keep that up!",
            "That's it! Perfect movement!",
            "Well done! Your form is improving!",
            "Nice! Stay focused like that!"
        ],
        senior: [
            "Excellent! Your form is very good!",
            "Well done! Keep that steady pace!",
            "Perfect! You're doing wonderfully!",
            "That's it! Steady and controlled!",
            "Very good! Keep it up!"
        ]
    },

    // ========== Encouragement (Form Needs Work) ==========
    needsWork: {
        young: [
            "Close! Try going a bit deeper!",
            "Almost there! You can do better!",
            "Good effort! Push a little more!",
            "Not bad! Let's perfect that form!",
            "Keep trying! You'll nail it!"
        ],
        middle: [
            "Good try! Focus on your form.",
            "Almost there! Take your time.",
            "Good effort! Let's refine that movement.",
            "You're getting there! Stay focused.",
            "Good attempt! Quality over quantity."
        ],
        senior: [
            "Good try! Take your time.",
            "That's okay! Go at your own pace.",
            "Well done for trying! Keep going.",
            "Good effort! Focus on control.",
            "You're doing fine! Stay steady."
        ]
    },

    // ========== Mid-Session Motivation ==========
    midSession: {
        young: [
            "Halfway there! Don't stop now! 💪",
            "You're crushing it! Keep the energy up!",
            "Looking strong! Finish strong! 🔥",
            "Keep that momentum going!",
            "You're in the zone! Don't quit!"
        ],
        middle: [
            "You're doing great! Keep going!",
            "Excellent progress! Stay focused!",
            "You're halfway there! Keep it up!",
            "Great work so far! Finish strong!",
            "Steady progress! You've got this!"
        ],
        senior: [
            "You're doing very well! Keep going!",
            "Wonderful progress! Continue like this!",
            "You're doing great! Take your time!",
            "Excellent work! Stay at your pace!",
            "Very good! You're doing wonderfully!"
        ]
    },

    // ========== Session Complete ==========
    sessionComplete: {
        young: [
            "Beast mode! Session crushed! 🏆",
            "BOOM! You killed it today! 💥",
            "Legendary session! You're unstoppable! 🚀",
            "That's what I'm talking about! 🔥",
            "You absolutely smashed that! Well done! 💪"
        ],
        middle: [
            "Excellent session! Well done!",
            "Great work! You should be proud!",
            "Session complete! You did great!",
            "Really good effort today!",
            "You completed it! Excellent job!"
        ],
        senior: [
            "Wonderful! You completed your session!",
            "Well done! You should be very proud!",
            "Excellent work today!",
            "You did it! That was wonderful!",
            "Great job! Your dedication is inspiring!"
        ]
    },

    // ========== Streak Messages ==========
    streakContinues: {
        young: [
            "Streak alive! Keep the fire burning! 🔥",
            "Consistency king/queen! Don't break it!",
            "On fire! {days} days straight! ⚡",
            "You're crushing this streak! {days} days!",
            "Unstoppable! {days} day streak! 💪"
        ],
        middle: [
            "Great consistency! {days} days in a row!",
            "Your dedication is paying off! {days} days!",
            "Excellent! {days} day streak maintained!",
            "{days} days strong! Keep it going!",
            "Impressive dedication! {days} days!"
        ],
        senior: [
            "Wonderful consistency! {days} days!",
            "Your dedication is admirable! {days} days!",
            "{days} days in a row! Well done!",
            "Excellent commitment! {days} days!",
            "Very impressive! {days} consecutive days!"
        ]
    },

    streakBroken: {
        young: [
            "Streak ended, but that's okay! Start fresh!",
            "No worries! Every champion has off days!",
            "Reset time! Let's build an even bigger streak!",
            "It happens! Get back on the grind!",
            "Fresh start! You got this! 💪"
        ],
        middle: [
            "That's alright! What matters is you're back!",
            "Starting fresh! Your commitment is what counts!",
            "Don't worry! Keep moving forward!",
            "You're here now, that's what matters!",
            "New streak starting today! Keep going!"
        ],
        senior: [
            "That's perfectly fine! You're back now!",
            "Don't worry! What matters is continuing!",
            "You're here today, that's wonderful!",
            "Starting fresh! Your dedication is inspiring!",
            "It's okay! Let's focus on today!"
        ]
    },

    // ========== Personal Best ==========
    personalBest: {
        young: [
            "NEW RECORD! You're a beast! 🏆",
            "Personal best! You're getting stronger! 💪",
            "That's what I'm talking about! New PB! 🚀",
            "Crushing your old records! Keep pushing! ⚡",
            "You just leveled up! New personal best! 🔥"
        ],
        middle: [
            "Personal best! Excellent progress!",
            "New record! Your hard work is paying off!",
            "Great achievement! You beat your best!",
            "Wonderful! You've improved!",
            "Impressive! New personal best!"
        ],
        senior: [
            "Wonderful! You've achieved a new personal best!",
            "Excellent! You've surpassed your previous best!",
            "Very impressive! You're making real progress!",
            "Well done! You've improved wonderfully!",
            "That's a great achievement! Personal best!"
        ]
    },

    // ========== Level Up ==========
    levelUp: {
        young: [
            "LEVEL UP! You're unstoppable! 🎮",
            "New level unlocked! Keep crushing it! 🚀",
            "You're leveling up! That's epic! ⚡",
            "DING! Level {level}! You're a beast! 💪",
            "Next level achieved! You're on fire! 🔥"
        ],
        middle: [
            "Congratulations! You've reached level {level}!",
            "Level up! Your progress is excellent!",
            "You've advanced to level {level}! Well done!",
            "Great milestone! Level {level} achieved!",
            "Wonderful progress! New level reached!"
        ],
        senior: [
            "Congratulations! You've reached level {level}!",
            "Wonderful achievement! New level!",
            "You've made excellent progress! Level {level}!",
            "Well done! You've advanced!",
            "That's wonderful! Level {level} achieved!"
        ]
    },

    // ========== Achievement Unlocked ==========
    achievementUnlocked: {
        young: [
            "Achievement unlocked! You're crushing it! 🏆",
            "Badge earned! Keep collecting them all! 🎯",
            "New achievement! You're a legend! ⭐",
            "Unlocked! That's what I'm talking about! 💪",
            "Achievement GET! You're on fire! 🔥"
        ],
        middle: [
            "Achievement unlocked! Well done!",
            "Congratulations! New badge earned!",
            "Great milestone achieved!",
            "You've unlocked a new achievement!",
            "Excellent! Badge earned!"
        ],
        senior: [
            "Congratulations! Achievement unlocked!",
            "Wonderful! You've earned a new badge!",
            "Excellent achievement! Well done!",
            "You've earned this achievement!",
            "Well done! New milestone reached!"
        ]
    },

    // ========== Consistency Praise ==========
    consistencyPraise: {
        young: [
            "Your consistency is insane! Keep it up! 🔥",
            "Showing up every day! That's champion mentality!",
            "Consistency = Results! You're proof! 💪",
            "This is how winners are made! Keep grinding!",
            "Your dedication is paying off! Don't stop!"
        ],
        middle: [
            "Your consistency is impressive!",
            "Showing up regularly is key! Well done!",
            "Your dedication is making a difference!",
            "Consistent effort brings results! Great work!",
            "Your commitment is commendable!"
        ],
        senior: [
            "Your dedication is truly admirable!",
            "Your consistent effort is wonderful!",
            "Regular practice is so important! Well done!",
            "Your commitment is inspiring!",
            "Consistency is key! You're doing wonderfully!"
        ]
    },

    // ========== Rest Day Suggestion ==========
    restSuggestion: {
        young: [
            "You've been grinding hard! Maybe rest tomorrow?",
            "Recovery is part of training! Consider a rest day!",
            "Beast mode activated! But recovery matters too!",
            "You're crushing it! Don't forget to rest!",
            "Awesome work! Your body might need a break soon!"
        ],
        middle: [
            "You've been very consistent! Consider a rest day.",
            "Great effort! Rest is important for recovery too.",
            "Excellent work! Listen to your body.",
            "You're doing great! Don't forget to rest.",
            "Wonderful commitment! Recovery days matter too."
        ],
        senior: [
            "You've been working very well! Rest is important.",
            "Wonderful effort! Please take care to rest.",
            "Excellent work! Remember to listen to your body.",
            "You're doing wonderfully! Rest days are important too.",
            "Great dedication! Please ensure adequate rest."
        ]
    }
};

// ============================================================================
// Message Selection Functions
// ============================================================================

/**
 * Get user's age group
 * 
 * @param {number} age - User's age
 * @returns {string} Age group ('young', 'middle', 'senior')
 */
function getAgeGroup(age) {
    if (age < 30) return 'young';
    if (age >= 60) return 'senior';
    return 'middle';
}

/**
 * Get random message from category
 * 
 * @param {string} category - Message category
 * @param {number} userAge - User's age
 * @param {Object} replacements - Key-value pairs for template replacement
 * @returns {string} Selected message
 */
export function getMotivationMessage(category, userAge = 40, replacements = {}) {
    const ageGroup = getAgeGroup(userAge);
    
    if (!motivationMessages[category] || !motivationMessages[category][ageGroup]) {
        return "Keep going! You're doing great!";
    }

    const messages = motivationMessages[category][ageGroup];
    let message = messages[Math.floor(Math.random() * messages.length)];

    // Replace template variables
    Object.keys(replacements).forEach(key => {
        message = message.replace(`{${key}}`, replacements[key]);
    });

    return message;
}

/**
 * Get session start message
 */
export function getSessionStartMessage(userAge = 40) {
    return getMotivationMessage('sessionStart', userAge);
}

/**
 * Get good form encouragement
 */
export function getGoodFormMessage(userAge = 40) {
    return getMotivationMessage('goodForm', userAge);
}

/**
 * Get encouragement for imperfect form
 */
export function getNeedsWorkMessage(userAge = 40) {
    return getMotivationMessage('needsWork', userAge);
}

/**
 * Get mid-session motivation
 */
export function getMidSessionMessage(userAge = 40) {
    return getMotivationMessage('midSession', userAge);
}

/**
 * Get session complete message
 */
export function getSessionCompleteMessage(userAge = 40, rpEarned = 0) {
    const baseMessage = getMotivationMessage('sessionComplete', userAge);
    return `${baseMessage} You earned ${rpEarned} RP!`;
}

/**
 * Get streak message
 */
export function getStreakMessage(streakDays, userAge = 40, broken = false) {
    const category = broken ? 'streakBroken' : 'streakContinues';
    return getMotivationMessage(category, userAge, { days: streakDays });
}

/**
 * Get personal best message
 */
export function getPersonalBestMessage(userAge = 40) {
    return getMotivationMessage('personalBest', userAge);
}

/**
 * Get level up message
 */
export function getLevelUpMessage(newLevel, userAge = 40) {
    return getMotivationMessage('levelUp', userAge, { level: newLevel });
}

/**
 * Get achievement unlocked message
 */
export function getAchievementMessage(achievementName, userAge = 40) {
    return getMotivationMessage('achievementUnlocked', userAge, { achievement: achievementName });
}

/**
 * Get consistency praise
 */
export function getConsistencyMessage(userAge = 40) {
    return getMotivationMessage('consistencyPraise', userAge);
}

/**
 * Get rest day suggestion
 */
export function getRestSuggestionMessage(userAge = 40) {
    return getMotivationMessage('restSuggestion', userAge);
}

// ============================================================================
// Context-Aware Messaging
// ============================================================================

/**
 * Get appropriate message based on performance
 * 
 * @param {Object} performanceData - Session performance metrics
 * @param {number} userAge - User's age
 * @returns {string} Contextual message
 */
export function getPerformanceMessage(performanceData, userAge = 40) {
    const {
        consistencyScore = 0,
        completionRate = 0,
        avgFormQuality = 0,
        isPersonalBest = false,
        sessionCount = 0
    } = performanceData;

    // Personal best takes priority
    if (isPersonalBest) {
        return getPersonalBestMessage(userAge);
    }

    // Excellent session
    if (consistencyScore >= 0.9 && completionRate >= 0.9) {
        return getGoodFormMessage(userAge);
    }

    // Good session
    if (consistencyScore >= 0.7 && completionRate >= 0.8) {
        return getMidSessionMessage(userAge);
    }

    // Needs improvement but encouraging
    if (completionRate >= 0.5) {
        return getNeedsWorkMessage(userAge);
    }

    // Default encouragement
    return "Keep going! Every session counts!";
}

/**
 * Get appropriate feedback during exercise
 * 
 * @param {Object} repData - Current rep data
 * @param {number} targetAngle - Target angle
 * @param {number} userAge - User's age
 * @returns {string} Real-time feedback message
 */
export function getRepFeedback(repData, targetAngle, userAge = 40) {
    const { angles } = repData;
    const avgAngle = angles.avg;
    const difference = Math.abs(avgAngle - targetAngle);

    if (difference <= 2) {
        return getGoodFormMessage(userAge);
    } else if (difference <= 10) {
        const ageGroup = getAgeGroup(userAge);
        if (ageGroup === 'young') {
            return "Almost perfect! Little bit more!";
        } else if (ageGroup === 'senior') {
            return "Very good! You're very close!";
        } else {
            return "Good! Almost there!";
        }
    } else {
        return getNeedsWorkMessage(userAge);
    }
}

/**
 * Get motivational message based on time of day
 * 
 * @param {number} userAge - User's age
 * @returns {string} Time-appropriate greeting
 */
export function getTimeBasedGreeting(userAge = 40) {
    const hour = new Date().getHours();
    const ageGroup = getAgeGroup(userAge);

    if (hour < 12) {
        return ageGroup === 'young' 
            ? "Morning grind! Let's get it! 🌅"
            : "Good morning! Ready to work on your recovery?";
    } else if (hour < 17) {
        return ageGroup === 'young'
            ? "Afternoon session! Let's go! ☀️"
            : "Good afternoon! Time for your exercises!";
    } else {
        return ageGroup === 'young'
            ? "Evening workout! Finish strong! 🌙"
            : "Good evening! Great time for your session!";
    }
}

/**
 * Suggest optimal session duration based on age and fitness
 * 
 * @param {number} userAge - User's age
 * @param {number} fitnessLevel - 1-5 scale
 * @returns {Object} Duration suggestion
 */
export function getSuggestedDuration(userAge, fitnessLevel = 3) {
    let baseDuration = 15; // minutes

    if (userAge < 30) {
        baseDuration = 20;
    } else if (userAge >= 60) {
        baseDuration = 10;
    }

    // Adjust for fitness level
    baseDuration += (fitnessLevel - 3) * 5;

    // Ensure reasonable bounds
    baseDuration = Math.max(10, Math.min(30, baseDuration));

    return {
        recommendedMinutes: baseDuration,
        minReps: baseDuration * 2,
        message: `Aim for ${baseDuration} minutes of focused exercise today!`
    };
}

// Export all functions
export default {
    getMotivationMessage,
    getSessionStartMessage,
    getGoodFormMessage,
    getNeedsWorkMessage,
    getMidSessionMessage,
    getSessionCompleteMessage,
    getStreakMessage,
    getPersonalBestMessage,
    getLevelUpMessage,
    getAchievementMessage,
    getConsistencyMessage,
    getRestSuggestionMessage,
    getPerformanceMessage,
    getRepFeedback,
    getTimeBasedGreeting,
    getSuggestedDuration
};
