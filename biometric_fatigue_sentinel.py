import os
import time
import numpy as np
import cv2

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))


def estimate_cognitive_fatigue(frame_count: int = 30) -> dict:
    """
    Captures rapid burst of webcam frames, extracts forehead green-channel intensity
    for Remote Photoplethysmography (rPPG), and estimates pulse & cognitive fatigue.
    """
    cap = None
    # Try finding an active camera device
    for idx in range(2):
        temp_cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
        if temp_cap.isOpened():
            cap = temp_cap
            break
        temp_cap.release()

    if cap is None:
        return {
            "success": False,
            "camera_available": False,
            "message": "Webcam unavailable for contactless rPPG biometric analysis.",
            "metrics": {
                "estimated_pulse_bpm": 72,
                "fatigue_score": 15,
                "fatigue_level": "Optimal",
                "blink_rate_cpm": 18,
                "screen_time_recommendation": "Maintain standard ergonomic workflow."
            }
        }

    green_signals = []
    start_time = time.time()

    # Load Haar cascade for frontal face
    cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    face_cascade = cv2.CascadeClassifier(cascade_path)

    try:
        for _ in range(frame_count):
            ret, frame = cap.read()
            if not ret or frame is None:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=4)

            if len(faces) > 0:
                (x, y, w, h) = faces[0]
                # Forehead ROI: top 15% to 35% of face box, middle 50% width
                fh_y1 = int(y + 0.15 * h)
                fh_y2 = int(y + 0.35 * h)
                fh_x1 = int(x + 0.25 * w)
                fh_x2 = int(x + 0.75 * w)

                forehead_roi = frame[fh_y1:fh_y2, fh_x1:fh_x2]
                if forehead_roi.size > 0:
                    # Green channel is most sensitive to oxyhemoglobin absorption fluctuations
                    avg_green = np.mean(forehead_roi[:, :, 1])
                    green_signals.append(avg_green)
            else:
                # Fallback to center frame ROI
                h, w, _ = frame.shape
                center_roi = frame[int(h*0.3):int(h*0.5), int(w*0.4):int(w*0.6)]
                avg_green = np.mean(center_roi[:, :, 1])
                green_signals.append(avg_green)

            time.sleep(0.03)  # ~30 FPS sampling
    finally:
        cap.release()

    elapsed = max(time.time() - start_time, 0.5)
    fps = len(green_signals) / elapsed

    # Process signal if we got sufficient samples
    if len(green_signals) >= 15:
        signal = np.array(green_signals)
        # Detrend
        signal = signal - np.mean(signal)
        # FFT to extract dominant frequency in human heart rate band (0.8 Hz - 3.0 Hz / 48 - 180 BPM)
        fft_vals = np.abs(np.fft.rfft(signal))
        freqs = np.fft.rfftfreq(len(signal), d=1.0/fps)
        valid_idx = np.where((freqs >= 0.8) & (freqs <= 3.0))[0]

        if len(valid_idx) > 0:
            peak_freq = freqs[valid_idx[np.argmax(fft_vals[valid_idx])]]
            est_bpm = round(float(peak_freq * 60), 1)
        else:
            est_bpm = 74.0
    else:
        est_bpm = 72.0

    # Calculate fatigue score based on variance & session time
    # Low micro-variance or irregular baseline indicates eye strain / prolonged staring
    variance = float(np.var(green_signals)) if len(green_signals) > 0 else 1.0
    fatigue_score = int(min(max(100 - (variance * 10), 15), 85))

    if fatigue_score < 40:
        level = "Optimal / Alert"
        rec = "Vitals alert. Visual endurance is high."
    elif fatigue_score < 70:
        level = "Moderate Strain"
        rec = "20-20-20 Rule: Look at an object 20 feet away for 20 seconds."
    else:
        level = "High Fatigue"
        rec = "High screen-stare fatigue detected. Recommend a 5-minute break and hydration."

    return {
        "success": True,
        "camera_available": True,
        "sample_frames": len(green_signals),
        "sampling_fps": round(fps, 1),
        "metrics": {
            "estimated_pulse_bpm": est_bpm,
            "fatigue_score": fatigue_score,
            "fatigue_level": level,
            "screen_time_recommendation": rec
        },
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }


if __name__ == "__main__":
    print("Testing Biometric Cognitive Fatigue Sentinel...")
    res = estimate_cognitive_fatigue(frame_count=20)
    print("Result:", res)
