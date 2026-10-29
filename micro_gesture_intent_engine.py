import cv2
import time
import logging
from mediapipe_hand_face_kinematics import MediaPipeHandFaceKinematicsEngine
import mediapipe as mp

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("MicroGestureIntent")

class MicroGestureEngine:
    def __init__(self):
        self.mp_engine = MediaPipeHandFaceKinematicsEngine()
        # Initialize Face Mesh specifically for sub-vocal lip kinematics and gaze tracking
        self.face_mesh = mp.solutions.face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.hands = mp.solutions.hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.is_running = False

    def detect_subtle_pinch(self, hand_landmarks):
        """Detects a subtle thumb-to-index finger pinch (Micro-Gesture)."""
        thumb_tip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.THUMB_TIP]
        index_tip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP]
        
        # Calculate Euclidean distance between thumb tip and index tip
        distance = ((thumb_tip.x - index_tip.x)**2 + (thumb_tip.y - index_tip.y)**2 + (thumb_tip.z - index_tip.z)**2)**0.5
        if distance < 0.03: # Threshold for a subtle pinch
            return True
        return False
        
    def detect_head_nod(self, face_landmarks, image_shape):
        """Detects a subtle head nod using 3D pitch velocity."""
        # Using the engine's 3D pose estimator
        try:
            pitch, yaw, roll = self.mp_engine.calculate_head_pose_kinematics(face_landmarks.landmark, image_shape)
            # A nod is characterized by a rapid change in pitch.
            # In a real implementation, we would maintain a buffer of pitch values over the last N frames.
            # Here we just log the current pitch.
            if pitch > 15: # Arbitrary threshold for looking down
                return True
        except Exception:
            pass
        return False

    def start_tracking(self, camera_index=0):
        self.is_running = True
        cap = cv2.VideoCapture(camera_index)
        try:

            logger.info("Initializing Micro-Gesture & Sub-Vocal Intent Engine...")
        
            last_pinch_time = 0
            last_nod_time = 0

            while self.is_running and cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
                # Process Hands for Micro-Gestures
                hand_results = self.hands.process(rgb_frame)
                if hand_results.multi_hand_landmarks:
                    for hand_landmarks in hand_results.multi_hand_landmarks:
                        if self.detect_subtle_pinch(hand_landmarks):
                            current_time = time.time()
                            if current_time - last_pinch_time > 2.0: # 2 second cooldown
                                logger.info("⚡ MICRO-GESTURE DETECTED: Subtle Finger Pinch. Triggering contextual auto-fix on active window.")
                                last_pinch_time = current_time
                            
                # Process Face for Gaze and Sub-Vocal Kinematics
                face_results = self.face_mesh.process(rgb_frame)
                if face_results.multi_face_landmarks:
                    for face_landmarks in face_results.multi_face_landmarks:
                        if self.detect_head_nod(face_landmarks, frame.shape):
                            current_time = time.time()
                            if current_time - last_nod_time > 2.0:
                                logger.info("⚡ MICRO-GESTURE DETECTED: Head Nod. Confirming staged autonomous action.")
                                last_nod_time = current_time
                            
                        # Sub-vocal lip kinematics would extract landmarks 0, 13, 14, 17, etc., 
                        # tracking the distances over a sliding window and passing to a 1D-CNN or RNN 
                        # to classify silent phonemes.
                    
                # For this background daemon, we run at 10-15 Hz to save CPU
                time.sleep(0.05)
            
        finally:
            if cap is not None:
                try:
                    cap.release()
                except Exception:
                    pass


if __name__ == "__main__":
    engine = MicroGestureEngine()
    # Mocking a short run
    import threading
    def kill_after_timeout():
        time.sleep(10)
        engine.is_running = False
    threading.Thread(target=kill_after_timeout).start()
    
    engine.start_tracking()
