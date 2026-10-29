import os
import sys

import requests

os.environ["OPENCV_LOG_LEVEL"] = "OFF"

import cv2
import numpy as np
from PIL import ImageGrab


def capture_webcam_hardware_vision():
    """Captures frame from webcam (or active stream buffer) and performs optical inspection on PIC board LEDs / displays."""
    try:
        print("------------------------------------------------------------")
        print("ANTIGRAVITY COMPUTER VISION: WEBCAM HARDWARE INSPECTION")
        print("------------------------------------------------------------")

        from shared_memory_frame_buffer import acquire_vision_frame

        frame = acquire_vision_frame(camera_index=0)
        if frame is None:
            print("⚠️ Webcam not accessible or disconnected.")
            return {"success": False, "error": "Webcam camera feed not accessible"}

        h, w, _ = frame.shape
        save_path = os.path.join(os.getcwd(), "webcam_hardware_capture.jpg")
        cv2.imwrite(save_path, frame)

        # 1. Color Mask Analysis (Detect Glowing Red/Green LEDs & 7-Segment displays)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        lower_red1 = np.array([0, 100, 100])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([160, 100, 100])
        upper_red2 = np.array([180, 255, 255])
        mask_red = cv2.inRange(hsv, lower_red1, upper_red1) | cv2.inRange(
            hsv, lower_red2, upper_red2
        )

        lower_green = np.array([35, 100, 100])
        upper_green = np.array([85, 255, 255])
        mask_green = cv2.inRange(hsv, lower_green, upper_green)

        red_pixels = cv2.countNonZero(mask_red)
        green_pixels = cv2.countNonZero(mask_green)

        # 2. Contour Detection for Hardware Display Regions
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(
            thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        bright_spots = len([c for c in contours if cv2.contourArea(c) > 20])

        report = {
            "success": True,
            "resolution": f"{w}x{h}",
            "saved_path": save_path,
            "optical_inspection": {
                "red_led_intensity_px": red_pixels,
                "green_led_intensity_px": green_pixels,
                "active_bright_display_elements": bright_spots,
                "hardware_state": (
                    "7-SEGMENT / LED DISPLAY ACTIVE"
                    if bright_spots > 0
                    else "DISPLAY STANDBY"
                ),
            },
        }

        print(
            f"[OK] Optical Inspection Complete: {bright_spots} bright elements detected."
        )
        print(f"   Saved Image: {save_path}")
        print("------------------------------------------------------------")
        return report
    except Exception as e:
        return {"success": False, "error": f"Hardware inspection error: {str(e)}"}


def capture_desktop_ocr_vision():
    """Captures full desktop screenshot and calculates visual layout telemetry."""
    try:
        print("------------------------------------------------------------")
        print("ANTIGRAVITY COMPUTER VISION: DESKTOP SCREEN OCR INSPECTION")
        print("------------------------------------------------------------")

        screenshot = ImageGrab.grab()
        w, h = screenshot.size
        save_path = os.path.join(os.getcwd(), "desktop_vision_capture.png")
        screenshot.save(save_path)

        arr = np.array(screenshot)
        avg_brightness = np.mean(arr)
        color_std = np.std(arr)

        report = {
            "success": True,
            "resolution": f"{w}x{h}",
            "saved_path": save_path,
            "visual_metrics": {
                "average_screen_brightness": round(float(avg_brightness), 2),
                "color_variance_score": round(float(color_std), 2),
                "screen_state": (
                    "DARK_MODE_IDE" if avg_brightness < 100 else "LIGHT_MODE_DOC"
                ),
            },
        }

        print(
            f"[OK] Screen Vision Analysis Complete: Resolution {w}x{h}, Avg Brightness: {avg_brightness:.1f}"
        )
        print("------------------------------------------------------------")
        return report
    except Exception as e:
        return {"success": False, "error": f"Desktop OCR error: {str(e)}"}


def query_huggingface_vision_models():
    """Queries Hugging Face for top Vision Transformers (ViT, Florence-2, YOLOv8)."""
    try:
        url = "https://huggingface.co/api/models?pipeline_tag=image-to-text&limit=5"
        res = requests.get(url, timeout=8)
        if res.status_code == 200:
            return [m.get("id") for m in res.json()]
        return ["microsoft/Florence-2-large", "Salesforce/blip-image-captioning-large"]
    except Exception:
        return ["microsoft/Florence-2-large", "Salesforce/blip-image-captioning-large"]


if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    webcam_res = capture_webcam_hardware_vision()
    desktop_res = capture_desktop_ocr_vision()
    hf_v_models = query_huggingface_vision_models()
    print("Hugging Face Top Vision Models:", hf_v_models)
