import base64
import os
import sys
import time

os.environ["OPENCV_LOG_LEVEL"] = "OFF"

import cv2
import numpy as np


class LiveCameraVisionEngine:
    def __init__(self, camera_index=0):
        self.camera_index = camera_index

    def capture_live_frame_analysis(self):
        """Captures a frame from live webcam (or in-memory stream buffer), performs real-time visual analysis, and returns Base64 frame + AI scene description."""
        from shared_memory_frame_buffer import acquire_vision_frame

        frame = acquire_vision_frame(camera_index=self.camera_index)
        if frame is None:
            return {
                "success": False,
                "error": "Webcam camera device not accessible or currently in use by another app.",
            }

        h, w, _ = frame.shape

        # 1. Real-time Motion / Brightness & Color Analysis
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        avg_brightness = np.mean(gray)

        # 2. HSV Color Segmentation for Hardware LEDs (Red / Green / Yellow)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        lower_red1 = np.array([0, 100, 100])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([160, 100, 100])
        upper_red2 = np.array([180, 255, 255])
        mask_red = cv2.inRange(hsv, lower_red1, upper_red1) | cv2.inRange(
            hsv, lower_red2, upper_red2
        )

        red_px = cv2.countNonZero(mask_red)

        # 3. Contour Detection for Objects & Displays
        _, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(
            thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        bright_objects = len([c for c in contours if cv2.contourArea(c) > 15])

        # 4. Generate AI Natural Language Visual Description
        scene_description = []
        scene_description.append(f"Camera Stream: {w}x{h} Resolution.")

        if avg_brightness > 140:
            scene_description.append("Environment is brightly lit.")
        elif avg_brightness < 60:
            scene_description.append("Environment has low ambient lighting.")
        else:
            scene_description.append("Environment lighting is normal.")

        if bright_objects > 0:
            scene_description.append(
                f"Detected {bright_objects} active glowing display/hardware segment(s)."
            )

        if red_px > 50:
            scene_description.append(
                f"Detected active Red LED / 7-Segment glow (Intensity: {red_px} px)."
            )

        ai_summary = " ".join(scene_description)

        # 5. Encode Frame to JPEG Base64 for web display
        _, buffer = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
        jpg_as_text = base64.b64encode(buffer).decode("utf-8")

        return {
            "success": True,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "resolution": f"{w}x{h}",
            "ai_scene_summary": ai_summary,
            "metrics": {
                "avg_brightness": round(float(avg_brightness), 1),
                "glowing_display_elements": bright_objects,
                "red_led_pixel_count": red_px,
            },
            "image_b64": f"data:image/jpeg;base64,{jpg_as_text}",
        }


if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    engine = LiveCameraVisionEngine()
    result = engine.capture_live_frame_analysis()
    print("------------------------------------------------------------")
    print("LIVE CAMERA VISION REAL-TIME STREAM TEST:")
    print("------------------------------------------------------------")
    print(f"Success: {result.get('success')}")
    print(f"Timestamp: {result.get('timestamp')}")
    print(f"AI Visual Summary: {result.get('ai_scene_summary')}")
    print("------------------------------------------------------------")
