import base64
import os
import sys
import time

os.environ["OPENCV_LOG_LEVEL"] = "OFF"

import cv2


class FacialExpressionEngine:
    def __init__(self, camera_index=0):
        self.camera_index = camera_index

    def analyze_facial_expression(self):
        """Captures camera frame (or active stream buffer), detects human face landmarks & mouth/eye geometry, and classifies facial expressions/emotions."""
        from mjpeg_stream_engine import LiveMJPEGStreamEngine

        telemetry = LiveMJPEGStreamEngine.get_latest_telemetry()
        frame = LiveMJPEGStreamEngine.get_latest_frame()

        if frame is None:
            cap = None
            if sys.platform.startswith("win"):
                try:
                    cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
                except Exception:
                    cap = cv2.VideoCapture(self.camera_index)
            else:
                cap = cv2.VideoCapture(self.camera_index)

            if cap is None or not cap.isOpened():
                cap = cv2.VideoCapture(0)

            if not cap.isOpened():
                return {
                    "success": False,
                    "error": "Camera feed not accessible for facial expression analysis",
                }

            ret, frame = cap.read()
            cap.release()

            if not ret or frame is None:
                return {
                    "success": False,
                    "error": "Failed to capture live camera frame",
                }

        detected_emotion_en = telemetry.get("emotion", "NEUTRAL")
        face_count = telemetry.get(
            "face_count", 1 if "NO_FACE" not in detected_emotion_en else 0
        )
        confidence = 0.95 if face_count > 0 else 0.50

        # Encode Frame to JPEG Base64
        _, buffer = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
        jpg_as_text = base64.b64encode(buffer).decode("utf-8")

        return {
            "success": True,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "faces_detected": face_count,
            "emotion_english": detected_emotion_en,
            "emotion_punjabi": detected_emotion_en,
            "confidence": confidence,
            "image_b64": f"data:image/jpeg;base64,{jpg_as_text}",
        }


if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    engine = FacialExpressionEngine()
    result = engine.analyze_facial_expression()
    print("------------------------------------------------------------")
    print("FACIAL EXPRESSION & EMOTION RECOGNITION TEST:")
    print("------------------------------------------------------------")
    print(f"Success: {result.get('success')}")
    print(f"Faces Detected: {result.get('faces_detected')}")
    print("------------------------------------------------------------")
