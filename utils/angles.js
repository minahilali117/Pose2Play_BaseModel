/**
 * Angle Calculation Utilities for Pose Estimation
 * 
 * These functions calculate angles between joints for exercise analysis.
 * Used for knee, hip, and shoulder angle measurements.
 */

/**
 * Calculates the angle (in degrees) between three points (a, b, and c) in 2D space.
 * The angle is measured at point `b`, where the line segments `a-b` and `b-c` form the angle.
 *
 * @param {Object} a The first point (a) (all points contain `x` and `y` coordinates).
 * @param {Object} b The central point (b), point where the angle is formed.
 * @param {Object} c The third point (c).
 * 
 * @returns {number} The angle in degrees (0° to 180°), between the three points.
 *                   If the calculated angle exceeds 180°, it is adjusted to fall within 0° to 180°.
 * 
 * @example
 * // Calculate knee angle (hip-knee-ankle)
 * const kneeAngle = calculateAngle(hipLandmark, kneeLandmark, ankleLandmark);
 * 
 * // Calculate hip angle (shoulder-hip-knee)
 * const hipAngle = calculateAngle(shoulderLandmark, hipLandmark, kneeLandmark);
 * 
 * // Calculate shoulder angle (ear-shoulder-elbow)
 * const shoulderAngle = calculateAngle(earLandmark, shoulderLandmark, elbowLandmark);
 */
export const calculateAngle = (a, b, c) => {
    const radians = Math.atan2(c.y - b.y, c.x - b.x) - Math.atan2(a.y - b.y, a.x - b.x);
    let angle = Math.abs(radians * 180.0 / Math.PI);
    if (angle > 180) angle = 360 - angle;
    return angle;
};

/**
 * MediaPipe Pose Landmark Indices Reference
 * Use these indices to access specific body landmarks from the pose detection results
 * 
 * UPPER BODY:
 * - 11: Left Shoulder
 * - 12: Right Shoulder
 * - 13: Left Elbow
 * - 14: Right Elbow
 * - 15: Left Wrist
 * - 16: Right Wrist
 * 
 * CORE/TORSO:
 * - 23: Left Hip
 * - 24: Right Hip
 * 
 * LOWER BODY:
 * - 25: Left Knee
 * - 26: Right Knee
 * - 27: Left Ankle
 * - 28: Right Ankle
 * - 29: Left Heel
 * - 30: Right Heel
 * - 31: Left Foot Index
 * - 32: Right Foot Index
 * 
 * HEAD:
 * - 0: Nose
 * - 7: Left Ear
 * - 8: Right Ear
 */
export const POSE_LANDMARKS = {
    // Head
    NOSE: 0,
    LEFT_EAR: 7,
    RIGHT_EAR: 8,
    
    // Upper body
    LEFT_SHOULDER: 11,
    RIGHT_SHOULDER: 12,
    LEFT_ELBOW: 13,
    RIGHT_ELBOW: 14,
    LEFT_WRIST: 15,
    RIGHT_WRIST: 16,
    
    // Core
    LEFT_HIP: 23,
    RIGHT_HIP: 24,
    
    // Lower body
    LEFT_KNEE: 25,
    RIGHT_KNEE: 26,
    LEFT_ANKLE: 27,
    RIGHT_ANKLE: 28,
    LEFT_HEEL: 29,
    RIGHT_HEEL: 30,
    LEFT_FOOT_INDEX: 31,
    RIGHT_FOOT_INDEX: 32
};

/**
 * Common angle calculation shortcuts for exercise analysis
 */
export const calculateKneeAngle = (landmarks, side = 'left') => {
    const hipIdx = side === 'left' ? POSE_LANDMARKS.LEFT_HIP : POSE_LANDMARKS.RIGHT_HIP;
    const kneeIdx = side === 'left' ? POSE_LANDMARKS.LEFT_KNEE : POSE_LANDMARKS.RIGHT_KNEE;
    const ankleIdx = side === 'left' ? POSE_LANDMARKS.LEFT_ANKLE : POSE_LANDMARKS.RIGHT_ANKLE;
    
    return calculateAngle(landmarks[hipIdx], landmarks[kneeIdx], landmarks[ankleIdx]);
};

export const calculateHipAngle = (landmarks, side = 'left') => {
    const shoulderIdx = side === 'left' ? POSE_LANDMARKS.LEFT_SHOULDER : POSE_LANDMARKS.RIGHT_SHOULDER;
    const hipIdx = side === 'left' ? POSE_LANDMARKS.LEFT_HIP : POSE_LANDMARKS.RIGHT_HIP;
    const kneeIdx = side === 'left' ? POSE_LANDMARKS.LEFT_KNEE : POSE_LANDMARKS.RIGHT_KNEE;
    
    return calculateAngle(landmarks[shoulderIdx], landmarks[hipIdx], landmarks[kneeIdx]);
};

export const calculateShoulderAngle = (landmarks, side = 'left') => {
    const earIdx = side === 'left' ? POSE_LANDMARKS.LEFT_EAR : POSE_LANDMARKS.RIGHT_EAR;
    const shoulderIdx = side === 'left' ? POSE_LANDMARKS.LEFT_SHOULDER : POSE_LANDMARKS.RIGHT_SHOULDER;
    const elbowIdx = side === 'left' ? POSE_LANDMARKS.LEFT_ELBOW : POSE_LANDMARKS.RIGHT_ELBOW;
    
    return calculateAngle(landmarks[earIdx], landmarks[shoulderIdx], landmarks[elbowIdx]);
};
