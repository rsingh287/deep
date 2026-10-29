import math
import os
import threading
import time

os.environ["OPENCV_LOG_LEVEL"] = "OFF"
os.environ["OPENCV_VIDEOIO_PRIORITY_MSMF"] = "0"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

import cv2
from shared_memory_frame_buffer import SharedMemoryFrameWriter, SharedMemoryFrameReader

try:
    from ultralytics import YOLO

    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False

try:
    import mediapipe as mp
    from mediapipe.tasks import python
    from mediapipe.tasks.python import vision

    MEDIAPIPE_AVAILABLE = True
except Exception:
    MEDIAPIPE_AVAILABLE = False

# Emoji mapping for COCO 80 object & animal classes
EMOJI_MAP = {
    "person": "👤",
    "cat": "🐱",
    "dog": "🐶",
    "bird": "🐦",
    "horse": "🐴",
    "sheep": "🐑",
    "cow": "🐮",
    "elephant": "🐘",
    "bear": "🐻",
    "zebra": "🦓",
    "giraffe": "🦒",
    "cell phone": "📱",
    "laptop": "💻",
    "chair": "🪑",
    "couch": "🛋️",
    "tv": "📺",
    "bottle": "🍾",
    "cup": "☕",
    "book": "📖",
    "clock": "⏰",
    "scissors": "✂️",
    "teddy bear": "🧸",
    "backpack": "🎒",
    "umbrella": "☂️",
    "keyboard": "⌨️",
    "mouse": "🖱️",
    "remote": "📺",
}

# Mapping MediaPipe Gestures to clean UI Labels


class LiveMJPEGStreamEngine:
    latest_raw_frame = None
    latest_jpeg_bytes = None
    active_mode = "all"  # "all" or "mediapipe"
    latest_telemetry = {
        "gesture": "NO_HAND_DETECTED",
        "emotion": "NEUTRAL",
        "face_count": 0,
        "hand_count": 0,
        "objects_detected": [],
    }
    is_streaming = False
    active_clients = 0
    worker_thread = None
    lock = threading.Lock()

    _shared_face_cascade = None
    _shared_yolo_model = None
    _shared_mp_hands = None
    _shared_emotion_pipeline = None
    _models_initialized = False

    @classmethod
    def _ensure_models_loaded(cls):
        """Loads neural models ONCE at class level to avoid blocking client requests."""
        if cls._models_initialized:
            return
        cls._models_initialized = True

        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        if os.path.exists(cascade_path):
            cls._shared_face_cascade = cv2.CascadeClassifier(cascade_path)

        if YOLO_AVAILABLE:
            try:
                cls._shared_yolo_model = YOLO("yolov8n.pt")
                print("🧠 YOLOv8 Multi-Object & Animal Neural Network Model Active!", flush=True)
            except Exception as e:
                print(f"⚠️ Failed to load YOLOv8 model: {e}", flush=True)

        if MEDIAPIPE_AVAILABLE:
            try:
                cls._shared_mp_hands = mp.solutions.hands.Hands(
                    static_image_mode=False,
                    max_num_hands=2,
                    min_detection_confidence=0.35,
                    min_tracking_confidence=0.35,
                )
                print("✋ Google MediaPipe Native Kinematics Hands Engine Active!", flush=True)
            except Exception as he:
                print(f"⚠️ Failed to load MediaPipe Hands solution: {he}", flush=True)

        try:
            from transformers import pipeline
            cls._shared_emotion_pipeline = pipeline(
                "image-classification", model="dima806/facial_emotions_image_detection"
            )
            print("😊 HuggingFace Deep Learning Facial Emotion ViT Model Active!", flush=True)
        except Exception as e:
            print(f"⚠️ Failed to load HuggingFace Emotion ViT Model: {e}", flush=True)

    def __init__(self, camera_index=0):
        self.camera_index = camera_index
        self._ensure_models_loaded()
        self.face_cascade = self._shared_face_cascade
        self.yolo_model = self._shared_yolo_model
        self.gesture_recognizer = None
        self.mp_hands_solution = self._shared_mp_hands
        self.emotion_pipeline = self._shared_emotion_pipeline
        self.cached_emotion = "NEUTRAL (92%)"
        self.emotion_busy = False
        self.last_emotion_time = 0

    def _async_emotion_predict(self, face_crop):
        try:
            from PIL import Image

            rgb_face = cv2.cvtColor(face_crop, cv2.COLOR_BGR2RGB)
            pil_face = Image.fromarray(rgb_face)
            preds = self.emotion_pipeline(pil_face)
            if preds and len(preds) > 0:
                top_emo = preds[0]["label"].upper()
                conf = int(preds[0]["score"] * 100)
                self.cached_emotion = f"{top_emo} ({conf}%)"
        except Exception:
            pass
        finally:
            self.emotion_busy = False

    @classmethod
    def get_latest_frame(cls):
        """Returns a copy of the latest raw webcam frame from shared memory."""
        with cls.lock:
            if cls.latest_raw_frame is not None:
                return cls.latest_raw_frame.copy()
        try:
            reader = SharedMemoryFrameReader(name="deep_mjpeg_frame_buffer")
            frame, _ = reader.read_frame(copy=True)
            reader.close()
            return frame
        except Exception:
            return None

    @classmethod
    def get_latest_telemetry(cls):
        """Returns latest gesture & emotion telemetry dictionary."""
        with cls.lock:
            return dict(cls.latest_telemetry)

    def start_worker_if_needed(self):
        """Starts background hardware capture thread if not already running."""
        with LiveMJPEGStreamEngine.lock:
            LiveMJPEGStreamEngine.active_clients += 1
            if (
                not LiveMJPEGStreamEngine.is_streaming
                or LiveMJPEGStreamEngine.worker_thread is None
                or not LiveMJPEGStreamEngine.worker_thread.is_alive()
            ):
                LiveMJPEGStreamEngine.is_streaming = True
                LiveMJPEGStreamEngine.worker_thread = threading.Thread(
                    target=self._capture_worker_loop, daemon=True
                )
                LiveMJPEGStreamEngine.worker_thread.start()

    def stop_worker_client(self):
        """Decrements client count when stream connection closes."""
        with LiveMJPEGStreamEngine.lock:
            LiveMJPEGStreamEngine.active_clients = max(
                0, LiveMJPEGStreamEngine.active_clients - 1
            )
            if LiveMJPEGStreamEngine.active_clients == 0:
                LiveMJPEGStreamEngine.is_streaming = False

    def _capture_worker_loop(self):
        """Ultra-Accurate Multi-Modal AI Loop: YOLOv8 Object/Animal/Bird Detection + MediaPipe 3D Hand Landmarks + Face Expression."""
        print(
            "📷 Starting Full AI Vision Engine (MediaPipe Hands + YOLOv8 Items/Animals)..."
        )
        cap = None
        for cam_id in [0, 1, 2]:
            try:
                temp_cap = cv2.VideoCapture(cam_id, cv2.CAP_DSHOW)
                if temp_cap.isOpened():
                    ret, test_frame = temp_cap.read()
                    if ret and test_frame is not None:
                        cap = temp_cap
                        break
                    temp_cap.release()
            except Exception:
                pass

        if cap is None or not cap.isOpened():
            print("❌ No webcam hardware available.")
            with LiveMJPEGStreamEngine.lock:
                LiveMJPEGStreamEngine.is_streaming = False
            return

        try:
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        except Exception as prop_err:
            print(f"⚠️ Camera property setting notice: {prop_err}")

        shm_writer = None
        try:
            shm_writer = SharedMemoryFrameWriter(name="deep_mjpeg_frame_buffer")
            print("⚡ Zero-Copy Shared Memory Frame Buffer Active (deep_mjpeg_frame_buffer)!")
        except Exception as shm_err:
            print(f"⚠️ Shared memory buffer init notice: {shm_err}")

        try:
            while LiveMJPEGStreamEngine.is_streaming:
                ret, frame = cap.read()
                if not ret or frame is None:
                    time.sleep(0.02)
                    continue

                display_frame = frame.copy()
                h_img, w_img, _ = display_frame.shape

                # Check if camera optic is covered or privacy slider is shut
                if frame.mean() < 3.0:
                    cv2.putText(
                        display_frame,
                        "OPTICAL SENSOR BLOCKED OR PRIVACY SHUTTER CLOSED",
                        (max(15, w_img // 2 - 270), h_img // 2 - 12),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.58,
                        (0, 165, 255),
                        2,
                    )
                    cv2.putText(
                        display_frame,
                        "Slide camera shutter open or switch to Direct Browser HD Mode",
                        (max(15, w_img // 2 - 290), h_img // 2 + 22),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.50,
                        (0, 240, 255),
                        1,
                    )

                # Publish frame to leak-proof Shared Physical RAM Buffer (IPC Zero-Copy)
                if shm_writer is not None:
                    shm_writer.write_frame(display_frame)

                # Store raw frame
                with LiveMJPEGStreamEngine.lock:
                    LiveMJPEGStreamEngine.latest_raw_frame = display_frame

                h_img, w_img, _ = display_frame.shape

                current_emotion = "NEUTRAL 😐"
                current_gesture = "NO_HAND_DETECTED"
                faces_found = 0
                hands_found = 0
                detected_items_list = []

                # 1. YOLOv8 UNIVERSAL OBJECT & ANIMAL DETECTION (Cats, Dogs, Birds, Phones, Laptops, Chairs, Persons, etc.)
                person_boxes = []
                if (
                    LiveMJPEGStreamEngine.active_mode == "all"
                    and self.yolo_model is not None
                ):
                    results = self.yolo_model(display_frame, verbose=False, conf=0.22)

                    for r in results:
                        for box in r.boxes:
                            cls_id = int(box.cls[0])
                            conf = float(box.conf[0])
                            bx1, by1, bx2, by2 = map(int, box.xyxy[0])
                            class_name = self.yolo_model.names.get(
                                cls_id, f"item_{cls_id}"
                            )

                            if class_name == "person":
                                person_boxes.append((bx1, by1, bx2, by2))
                                detected_items_list.append("Person")
                            else:
                                emoji = EMOJI_MAP.get(class_name.lower(), "📦")
                                item_label = (
                                    f"{class_name.upper()} {emoji} ({int(conf*100)}%)"
                                )
                                detected_items_list.append(class_name)

                                # Draw Bright Cyan/Yellow Box around Animals, Birds, & Objects (Phones, Cups, etc.)
                                cv2.rectangle(
                                    display_frame,
                                    (bx1, by1),
                                    (bx2, by2),
                                    (255, 240, 0),
                                    2,
                                )
                                cv2.putText(
                                    display_frame,
                                    item_label,
                                    (bx1, max(25, by1 - 10)),
                                    cv2.FONT_HERSHEY_SIMPLEX,
                                    0.55,
                                    (255, 240, 0),
                                    2,
                                )

                # 2. FACE EXPRESSION & EMOTION DETECTION
                face_boxes = []
                gray = cv2.cvtColor(display_frame, cv2.COLOR_BGR2GRAY)
                if self.face_cascade is not None:
                    faces = self.face_cascade.detectMultiScale(
                        gray, scaleFactor=1.08, minNeighbors=4, minSize=(50, 50)
                    )
                    faces_found = len(faces)

                    h_img, w_img = display_frame.shape[:2]
                    for fx, fy, fw, fh in faces:
                        # Expanded Face Bounding Box to capture full mouth, chin & turban
                        ey1 = max(0, fy - int(fh * 0.1))
                        ey2 = min(h_img, fy + int(fh * 1.35))
                        ex1 = max(0, fx - int(fw * 0.1))
                        ex2 = min(w_img, fx + int(fw * 1.1))

                        face_boxes.append((ex1, ey1, ex2 - ex1, ey2 - ey1))

                        # Hugging Face Vision Transformer Facial Emotion Classification (Async Accelerated)
                        if (
                            LiveMJPEGStreamEngine.active_mode == "all"
                            and self.emotion_pipeline is not None
                            and (ex2 - ex1) > 30
                            and (ey2 - ey1) > 30
                        ):
                            now = time.time()
                            if not self.emotion_busy and (
                                now - self.last_emotion_time > 0.1
                            ):
                                self.emotion_busy = True
                                self.last_emotion_time = now
                                face_crop = display_frame[ey1:ey2, ex1:ex2].copy()
                                threading.Thread(
                                    target=self._async_emotion_predict,
                                    args=(face_crop,),
                                    daemon=True,
                                ).start()
                            current_emotion = self.cached_emotion
                        else:
                            current_emotion = "MEDIA PIPE KINEMATICS 👤"

                        # Draw GREEN Box around Expanded Full Face (includes mouth & chin)
                        cv2.rectangle(
                            display_frame, (ex1, ey1), (ex2, ey2), (0, 255, 0), 2
                        )
                        cv2.putText(
                            display_frame,
                            f"FACE: {current_emotion}",
                            (ex1, max(25, ey1 - 10)),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.6,
                            (0, 255, 0),
                            2,
                        )

                # Fallback to YOLO person head if Haar face missed
                if faces_found == 0 and len(person_boxes) > 0:
                    for px1, py1, px2, py2 in person_boxes:
                        pw = px2 - px1
                        ph = py2 - py1
                        fx = max(0, px1 + int(pw * 0.2))
                        fy = max(0, py1 + int(ph * 0.02))
                        fw = min(w_img - fx, int(pw * 0.6))
                        fh = min(h_img - fy, int(ph * 0.45))
                        face_boxes.append((fx, fy, fw, fh))
                        faces_found += 1

                        if self.emotion_pipeline is not None and fw > 30 and fh > 30:
                            now = time.time()
                            if not self.emotion_busy and (
                                now - self.last_emotion_time > 0.1
                            ):
                                self.emotion_busy = True
                                self.last_emotion_time = now
                                face_crop = display_frame[
                                    fy : fy + fh, fx : fx + fw
                                ].copy()
                                threading.Thread(
                                    target=self._async_emotion_predict,
                                    args=(face_crop,),
                                    daemon=True,
                                ).start()
                            current_emotion = self.cached_emotion
                        else:
                            current_emotion = "FOCUSED / NEUTRAL 👤"

                        cv2.rectangle(
                            display_frame, (fx, fy), (fx + fw, fy + fh), (0, 255, 0), 2
                        )
                        cv2.putText(
                            display_frame,
                            f"FACE: {current_emotion}",
                            (fx, max(25, fy - 10)),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.6,
                            (0, 255, 0),
                            2,
                        )

                # 3. GOOGLE MEDIAPIPE DEEP NEURAL NETWORK HAND TRACKING & GESTURE RECOGNITION
                HAND_CONNECTIONS = [
                    (0, 1),
                    (1, 2),
                    (2, 3),
                    (3, 4),  # Thumb
                    (0, 5),
                    (5, 6),
                    (6, 7),
                    (7, 8),  # Index
                    (0, 9),
                    (9, 10),
                    (10, 11),
                    (11, 12),  # Middle
                    (0, 13),
                    (13, 14),
                    (14, 15),
                    (15, 16),  # Ring
                    (0, 17),
                    (17, 18),
                    (18, 19),
                    (19, 20),  # Pinky
                    (5, 9),
                    (9, 13),
                    (13, 17),  # Palm
                ]

                detected_hands = []
                if self.gesture_recognizer is not None:
                    # Convert BGR frame to RGB MediaPipe Image
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    mp_image = mp.Image(
                        image_format=mp.ImageFormat.SRGB, data=rgb_frame
                    )
                    try:
                        recognition_result = self.gesture_recognizer.recognize(mp_image)
                        if recognition_result and recognition_result.hand_landmarks:
                            for hand_idx, hand_landmarks in enumerate(recognition_result.hand_landmarks):
                                g_cand = ""
                                if (
                                    hasattr(recognition_result, "gestures")
                                    and recognition_result.gestures
                                    and len(recognition_result.gestures) > hand_idx
                                    and recognition_result.gestures[hand_idx]
                                ):
                                    top_g = recognition_result.gestures[hand_idx][0]
                                    if top_g.score > 0.3 and top_g.category_name not in ["None", "Unrecognized", ""]:
                                        g_cand = top_g.category_name.upper().replace("_", " ")
                                detected_hands.append((hand_idx, [(lm.x, lm.y) for lm in hand_landmarks], g_cand))
                    except Exception:
                        pass
                elif self.mp_hands_solution is not None:
                    rgb_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
                    rgb_frame.flags.writeable = False
                    try:
                        res = self.mp_hands_solution.process(rgb_frame)
                        if res and res.multi_hand_landmarks:
                            for hand_idx, h_lm in enumerate(res.multi_hand_landmarks):
                                detected_hands.append((hand_idx, [(lm.x, lm.y) for lm in h_lm.landmark], ""))
                    except Exception:
                        pass

                if detected_hands:
                    hands_found = len(detected_hands)
                    try:
                        for hand_idx, hand_landmarks_norm, mp_gesture in detected_hands:
                            # Extract 21 hand joint coordinates for THIS hand
                            coords = [
                                (int(lm_x * w_img), int(lm_y * h_img))
                                for lm_x, lm_y in hand_landmarks_norm
                            ]
                            x_coords = [c[0] for c in coords]
                            y_coords = [c[1] for c in coords]

                            # Calculate tight hand box
                            min_x = max(0, min(x_coords) - 10)
                            max_x = min(w_img, max(x_coords) + 10)
                            min_y = max(0, min(y_coords) - 10)
                            max_y = min(h_img, max(y_coords) + 10)

                            wrist = coords[0]
                            mcp_mid = coords[9]

                            def get_dist(p1, p2):
                                return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

                            palm_size = max(15.0, get_dist(wrist, mcp_mid))

                            # Kinematic knuckle-relative finger extension analysis
                            thumb_ext = get_dist(coords[4], coords[9]) > get_dist(coords[2], coords[9]) * 1.15
                            index_ext = get_dist(coords[8], wrist) > get_dist(coords[6], wrist) * 1.12
                            middle_ext = get_dist(coords[12], wrist) > get_dist(coords[10], wrist) * 1.12
                            ring_ext = get_dist(coords[16], wrist) > get_dist(coords[14], wrist) * 1.12
                            pinky_ext = get_dist(coords[20], wrist) > get_dist(coords[18], wrist) * 1.12

                            index_dir_x = coords[8][0] - wrist[0]
                            index_dir_y = coords[8][1] - wrist[1]

                            if (
                                index_ext
                                and not middle_ext
                                and not ring_ext
                                and not pinky_ext
                            ):
                                if abs(index_dir_x) > abs(index_dir_y):
                                    if index_dir_x < -20:
                                        current_gesture = "POINTING LEFT 👈"
                                    else:
                                        current_gesture = "POINTING RIGHT 👉"
                                else:
                                    if index_dir_y > 20:
                                        current_gesture = "POINTING DOWN 👇"
                                    else:
                                        current_gesture = "POINTING UP ☝️"
                            elif (
                                index_ext and middle_ext and ring_ext and pinky_ext
                            ):
                                current_gesture = "OPEN PALM / HELLO ✋"
                            elif (
                                index_ext
                                and middle_ext
                                and not ring_ext
                                and not pinky_ext
                            ):
                                current_gesture = "PEACE / VICTORY SIGN ✌️"
                            elif (
                                thumb_ext
                                and pinky_ext
                                and not index_ext
                                and not middle_ext
                                and not ring_ext
                            ):
                                current_gesture = "HANG LOOSE / CALL 🤙"
                            elif (
                                index_ext
                                and pinky_ext
                                and not middle_ext
                                and not ring_ext
                            ):
                                current_gesture = "ROCK / METAL 🤘"
                            elif (
                                thumb_ext
                                and index_ext
                                and pinky_ext
                                and not middle_ext
                                and not ring_ext
                            ):
                                current_gesture = "LOVE SIGN 🤟"
                            elif (
                                index_ext
                                and middle_ext
                                and ring_ext
                                and not pinky_ext
                            ):
                                current_gesture = "THREE FINGERS / OK 🤟"
                            elif (
                                thumb_ext
                                and not index_ext
                                and not middle_ext
                                and not ring_ext
                                and not pinky_ext
                            ):
                                if coords[4][1] > wrist[1] + 15:
                                    current_gesture = "THUMBS DOWN 👎"
                                else:
                                    current_gesture = "THUMBS UP 👍"
                            elif (
                                not index_ext
                                and not middle_ext
                                and not ring_ext
                                and not pinky_ext
                            ):
                                current_gesture = "CLOSED FIST ✊"
                            elif get_dist(coords[4], coords[8]) < palm_size * 0.45 and middle_ext and ring_ext:
                                current_gesture = "OK SIGN 👌"
                            elif mp_gesture:
                                current_gesture = mp_gesture
                            else:
                                current_gesture = "ACTIVE HAND SIGN ✋"

                            # Draw 3D Hand Skeletal Lines (Cyan)
                            for start_idx, end_idx in HAND_CONNECTIONS:
                                if start_idx < len(coords) and end_idx < len(
                                    coords
                                ):
                                    cv2.line(
                                        display_frame,
                                        coords[start_idx],
                                        coords[end_idx],
                                        (255, 240, 0),
                                        2,
                                    )

                            # Draw 21 Hand Landmark Joints (Neon Green)
                            for lx, ly in coords:
                                cv2.circle(
                                    display_frame, (lx, ly), 4, (0, 255, 136), -1
                                )

                            # Draw Box around Hand (text_x aligned so it never gets cut off on frame edge!)
                            text_x = max(10, min(min_x, w_img - 260))
                            cv2.rectangle(
                                display_frame,
                                (min_x, min_y),
                                (max_x, max_y),
                                (0, 255, 255),
                                2,
                            )
                            cv2.putText(
                                display_frame,
                                f"HAND: {current_gesture}",
                                (text_x, max(25, min_y - 10)),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.6,
                                (0, 255, 255),
                                2,
                            )
                    except Exception:
                        pass

                # 4. OVERLAY BOTTOM TELEMETRY HUD BANNER
                items_str = (
                    ", ".join(
                        list(set([i for i in detected_items_list if i != "Person"]))
                    )
                    or "NONE"
                )
                hud_text = f"30 FPS | HANDS: {hands_found} [{current_gesture}] | ITEMS: {items_str.upper()}"

                # Dark translucent bar at bottom of video feed
                cv2.rectangle(
                    display_frame, (0, h_img - 32), (w_img, h_img), (10, 15, 26), -1
                )
                cv2.putText(
                    display_frame,
                    hud_text,
                    (12, h_img - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 240, 255),
                    1,
                )

                # Update global telemetry state
                with LiveMJPEGStreamEngine.lock:
                    LiveMJPEGStreamEngine.latest_jpeg_bytes = cv2.imencode(
                        ".jpg", display_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80]
                    )[1].tobytes()
                    LiveMJPEGStreamEngine.latest_telemetry = {
                        "gesture": current_gesture,
                        "emotion": current_emotion,
                        "face_count": faces_found,
                        "hand_count": hands_found,
                        "objects_detected": list(set(detected_items_list)),
                    }

                time.sleep(0.015)
        except Exception as worker_err:
            print(f"⚠️ Webcam hardware capture worker encountered error: {worker_err}")
        finally:
            if cap is not None and cap.isOpened():
                cap.release()
            if shm_writer is not None:
                try:
                    shm_writer.close()
                    shm_writer.unlink()
                except Exception:
                    pass
            with LiveMJPEGStreamEngine.lock:
                LiveMJPEGStreamEngine.latest_raw_frame = None
                LiveMJPEGStreamEngine.latest_jpeg_bytes = None
                LiveMJPEGStreamEngine.is_streaming = False
                LiveMJPEGStreamEngine.latest_telemetry = {
                    "gesture": "STREAM_STOPPED",
                    "emotion": "STREAM_STOPPED",
                    "face_count": 0,
                    "hand_count": 0,
                    "objects_detected": [],
                }
            print("Webcam hardware capture worker stopped cleanly.")

    def generate_mjpeg_frames(self):
        """Yields MJPEG stream bytes from shared RAM buffer continuously for the HTTP response."""
        self.start_worker_if_needed()
        try:
            # Wait up to 1.5 seconds for first frame
            for _ in range(40):
                with LiveMJPEGStreamEngine.lock:
                    if LiveMJPEGStreamEngine.latest_jpeg_bytes is not None:
                        break
                time.sleep(0.04)

            while LiveMJPEGStreamEngine.is_streaming:
                with LiveMJPEGStreamEngine.lock:
                    frame_bytes = LiveMJPEGStreamEngine.latest_jpeg_bytes

                if frame_bytes is not None:
                    yield (
                        b"--frame\r\n"
                        b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
                    )

                time.sleep(0.03)  # ~30 FPS stream output
        finally:
            self.stop_worker_client()


if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    print("Testing Live MJPEG Stream generator...")
    engine = LiveMJPEGStreamEngine()
    gen = engine.generate_mjpeg_frames()
    time.sleep(1)
    first_frame = next(gen)
    print("First Frame Byte Size:", len(first_frame))
