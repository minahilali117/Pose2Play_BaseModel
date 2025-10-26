/**
 * Pose Detector using MediaPipe Tasks Vision
 * 
 * This module provides pose detection functionality using Google's MediaPipe.
 * It loads a pre-trained pose estimation model and detects human poses in real-time video.
 * 
 * IMPORTANT: This is NOT a trainable ML model. MediaPipe uses a pre-trained deep learning
 * model that cannot be retrained. Instead, you customize RULES and THRESHOLDS for different
 * exercises based on the pose landmarks detected.
 */

import { FilesetResolver, PoseLandmarker, DrawingUtils } from "@mediapipe/tasks-vision";

// Path to the pose landmarker model file
// You can use either 'lite' (faster, less accurate) or 'full' (slower, more accurate)
const MODEL_PATH = "../models/pose_landmarker_lite.task";

// Pose connections for drawing skeleton (excluding face landmarks)
const POSE_CONNECTIONS_NON_FACE = [
  { start: 11, end: 12 }, // Shoulders
  { start: 12, end: 14 }, // Right shoulder to elbow
  { start: 14, end: 16 }, // Right elbow to wrist
  { start: 11, end: 13 }, // Left shoulder to elbow
  { start: 13, end: 15 }, // Left elbow to wrist
  { start: 11, end: 23 }, // Left shoulder to hip
  { start: 12, end: 24 }, // Right shoulder to hip
  { start: 23, end: 24 }, // Hips
  { start: 23, end: 25 }, // Left hip to knee
  { start: 24, end: 26 }, // Right hip to knee
  { start: 25, end: 27 }, // Left knee to ankle
  { start: 26, end: 28 }, // Right knee to ankle
  { start: 27, end: 29 }, // Left ankle to heel
  { start: 28, end: 30 }, // Right ankle to heel
  { start: 29, end: 31 }, // Left heel to foot
  { start: 30, end: 32 }, // Right heel to foot
];

let poseLandmarker;
let enableTwoPoses = false;

/**
 * Enable or disable two-person pose detection
 * @param {boolean} enable - Whether to detect two poses
 */
export function setEnableTwoPoses(enable) {
  enableTwoPoses = enable;
  if (poseLandmarker) {
    poseLandmarker.close();
    poseLandmarker = null;
  }
  createPoseLandmarker();
}

/**
 * Creates and initializes the pose landmarker
 * Loads the MediaPipe WASM runtime and model file
 */
async function createPoseLandmarker() {
  try {
    // Load MediaPipe Vision tasks WASM runtime from CDN
    const vision = await FilesetResolver.forVisionTasks(
      "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.21/wasm"
    );
    
    // Create pose landmarker with model
    poseLandmarker = await PoseLandmarker.createFromOptions(vision, {
      baseOptions: { modelAssetPath: MODEL_PATH },
      runningMode: "VIDEO", // Use VIDEO mode for real-time webcam
      numPoses: enableTwoPoses ? 2 : 1, // Number of poses to detect
    });
  } catch (e) {
    console.error("ERROR initializing pose landmarker:", e);
  }
  return poseLandmarker;
}

/**
 * Main pose detection function for real-time video
 * 
 * @param {Object} webcamRef - React ref to video element
 * @param {Object} canvasRef - React ref to canvas element for drawing
 * @param {Function} onResultCallback - Callback function that receives detected landmarks
 * @param {boolean} drawSkeleton - Whether to draw skeleton on canvas
 * @returns {Object} The pose landmarker instance
 */
const detectPose = async (webcamRef, canvasRef, onResultCallback, drawSkeleton = true) => {
  if (!poseLandmarker) {
    poseLandmarker = await createPoseLandmarker();
  }
  
  let animationID;

  const detectAndDraw = () => {
    if (webcamRef.current && webcamRef.current.video.readyState >= 2) {
      try {
        // Detect pose in current video frame
        poseLandmarker.detectForVideo(webcamRef.current.video, performance.now(), (result) => {
          if (!result || !result.landmarks || result.landmarks.length === 0) return;
          
          const canvas = canvasRef.current;
          const canvasCtx = canvas.getContext("2d");
          const drawingUtils = new DrawingUtils(canvasCtx);
          let sortedLandmarks = result.landmarks;

          canvasCtx.save();
          canvasCtx.clearRect(0, 0, canvas.width, canvas.height);
          
          // Draw video frame
          canvasCtx.drawImage(webcamRef.current.video, 0, 0, canvas.width, canvas.height);

          // Sort landmarks by x-position if detecting two people
          if (result.landmarks.length === 2) {
            sortedLandmarks = result.landmarks.sort((a, b) => {
              if (a[11] && b[11]) return a[11].x - b[11].x;
              return 0;
            });
          }

          // Draw skeleton for each detected pose
          if (drawSkeleton) {
            for (let i = 0; i < sortedLandmarks.length; i++) {
              const pose = sortedLandmarks[i];
              if (pose) {
                // Filter out face landmarks (indices 0-10 and 17-22)
                const nonFaceLandmarks = pose.filter((_, index) => index > 10 && (index < 17 || index > 22));
                
                // Draw landmarks (joints)
                drawingUtils.drawLandmarks(nonFaceLandmarks, { 
                  color: i === 0 ? "red" : "purple", 
                  radius: 2.5 
                });
                
                // Draw connections (skeleton)
                drawingUtils.drawConnectors(pose, POSE_CONNECTIONS_NON_FACE, {
                  color: i === 0 ? "blue" : "orange",
                  lineWidth: 5,
                });
              }
            }
          }

          canvasCtx.restore();
          
          // Send landmarks to callback for processing
          if (!enableTwoPoses && result.landmarks[0]) {
            onResultCallback(result.landmarks[0]);
          } else if (enableTwoPoses && result.landmarks.length === 2) {
            onResultCallback(result.landmarks[0], result.landmarks[1]);
          }
        });
      } catch (e) {
        console.error("Pose detection error:", e);
      }
    }
    
    // Continue detection loop
    animationID = requestAnimationFrame(detectAndDraw);
    return () => cancelAnimationFrame(animationID);
  };

  detectAndDraw();
  return poseLandmarker;
};

export default detectPose;
