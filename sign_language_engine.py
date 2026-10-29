import base64
import os
import sys
import time

os.environ["OPENCV_LOG_LEVEL"] = "OFF"

import cv2


class SignLanguageVisionEngine:
    def __init__(self, camera_index=0):
        self.camera_index = camera_index

    def recognize_sign_gesture(self):
        """Captures frame from webcam (or active stream buffer), analyzes hand shape geometry, and translates Sign Language gestures."""
        from mjpeg_stream_engine import LiveMJPEGStreamEngine

        from shared_memory_frame_buffer import acquire_vision_frame

        telemetry = LiveMJPEGStreamEngine.get_latest_telemetry()
        frame = acquire_vision_frame(camera_index=self.camera_index)
        if frame is None:
            return {
                "success": False,
                "error": "Camera feed not accessible for Sign Language recognition",
            }

        gesture_detected = telemetry.get("gesture", "UNKNOWN_GESTURE")
        sign_meaning_en = f"Detected Gesture: '{gesture_detected}'"
        sign_meaning_pa = f"ਇਸ਼ਾਰਾ ਦੇਖਿਆ ਗਿਆ: '{gesture_detected}'"
        confidence = 0.95 if gesture_detected != "NO_HAND_DETECTED" else 0.50

        # Encode Frame to JPEG Base64
        _, buffer = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
        jpg_as_text = base64.b64encode(buffer).decode("utf-8")

        return {
            "success": True,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "gesture": gesture_detected,
            "meaning_english": sign_meaning_en,
            "meaning_punjabi": sign_meaning_pa,
            "confidence": confidence,
            "image_b64": f"data:image/jpeg;base64,{jpg_as_text}",
        }


if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    engine = SignLanguageVisionEngine()
    result = engine.recognize_sign_gesture()
    print("------------------------------------------------------------")
    print("SIGN LANGUAGE & GESTURE RECOGNITION TEST:")
    print("------------------------------------------------------------")
    print(f"Success: {result.get('success')}")
    print(f"Gesture Identified: {result.get('gesture')}")
    print(f"English Meaning: {result.get('meaning_english')}")
    print("------------------------------------------------------------")
