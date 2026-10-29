import os
import sys
import time
import traceback

import requests
from dotenv import load_dotenv

# Ensure we're in the right directory and have access to the engine
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import autonomous_intent_engine

# Load environment variables
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()

if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
    print("==========================================================")
    print("⚠️ WARNING: TELEGRAM_BOT_TOKEN is missing or invalid in .env")
    print("Please add your token to the .env file to use the Telegram Bot.")
    print("==========================================================")
    sys.exit(1)

BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

SURVEILLANCE_KEYBOARD = {
    "inline_keyboard": [
        [
            {"text": "📷 Room Photo", "callback_data": "cmd_room_photo"},
            {"text": "🎥 5s Video Clip", "callback_data": "cmd_room_video"},
        ],
        [
            {"text": "🩺 System Health", "callback_data": "cmd_system_health"},
            {"text": "📊 Daily Report", "callback_data": "cmd_daily_report"},
        ],
        [
            {"text": "🛡️ Sentinel ON", "callback_data": "cmd_sentinel_on"},
            {"text": "🛑 Sentinel OFF", "callback_data": "cmd_sentinel_off"},
        ],
    ]
}


def send_message(
    chat_id: int, text: str, show_keyboard: bool = False, reply_markup: dict = None
):
    """Sends a text message back to Telegram user, chunking if it exceeds limits."""
    url = f"{BASE_URL}/sendMessage"

    # Telegram max message length is 4096
    MAX_LENGTH = 4000

    chunks = [text[i : i + MAX_LENGTH] for i in range(0, len(text), MAX_LENGTH)]

    for i, chunk in enumerate(chunks):
        payload = {"chat_id": chat_id, "text": chunk, "parse_mode": "Markdown"}

        # Only attach keyboards to the final chunk
        if i == len(chunks) - 1:
            if reply_markup:
                payload["reply_markup"] = reply_markup
            elif show_keyboard:
                payload["reply_markup"] = SURVEILLANCE_KEYBOARD

        try:
            res = requests.post(url, json=payload, timeout=10)
            if res.status_code != 200:
                # Fallback without markdown if there's a parsing error
                payload.pop("parse_mode", None)
                requests.post(url, json=payload, timeout=10)
        except Exception as e:
            print(f"[TelegramService] Error sending message chunk: {e}")


def answer_callback_query(callback_query_id: str, text: str = ""):
    url = f"{BASE_URL}/answerCallbackQuery"
    try:
        payload = {"callback_query_id": callback_query_id, "text": text}
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"[TelegramService] Callback query answer error: {e}")


def send_photo(
    chat_id: int, photo_path: str, caption: str = "", reply_markup: dict = None
):
    url = f"{BASE_URL}/sendPhoto"
    try:
        with open(photo_path, "rb") as f:
            files = {"photo": f}
            data = {"chat_id": chat_id, "caption": caption, "parse_mode": "Markdown"}
            if reply_markup:
                data["reply_markup"] = reply_markup
            res = requests.post(url, data=data, files=files, timeout=30)
            if res.status_code != 200:
                data.pop("parse_mode", None)
                requests.post(url, data=data, files=files, timeout=30)
    except Exception as e:
        print(f"[TelegramService] Error sending photo: {e}")
        send_message(chat_id, f"⚠️ Error sending photo: {e}")


def send_video(chat_id: int, video_path: str, caption: str = ""):
    url = f"{BASE_URL}/sendVideo"
    try:
        with open(video_path, "rb") as f:
            files = {"video": f}
            data = {"chat_id": chat_id, "caption": caption}
            requests.post(url, data=data, files=files, timeout=60)
    except Exception as e:
        print(f"[TelegramService] Error sending video: {e}")
        send_message(chat_id, f"⚠️ Error sending video: {e}")


def download_telegram_file(file_id: str, suffix: str) -> str:
    url = f"{BASE_URL}/getFile?file_id={file_id}"
    try:
        res = requests.get(url, timeout=15)
        if res.status_code == 200:
            file_path = res.json()["result"]["file_path"]
            dl_url = (
                f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_path}"
            )
            img_data = requests.get(dl_url, timeout=60).content
            import uuid

            temp_dir = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "temp_media")
            )
            os.makedirs(temp_dir, exist_ok=True)
            local_path = os.path.join(temp_dir, f"dl_{uuid.uuid4().hex[:8]}{suffix}")
            with open(local_path, "wb") as f:
                f.write(img_data)
            return local_path
    except Exception as e:
        print(f"[TelegramService] Download error: {e}")
    return ""


def query_ollama_vision(image_path: str, prompt: str) -> str:
    import base64

    try:
        with open(image_path, "rb") as img_file:
            img_b64 = base64.b64encode(img_file.read()).decode("utf-8")
        url = "http://localhost:11434/api/generate"
        payload = {
            "model": "qwen2.5vl:7b",
            "prompt": prompt,
            "images": [img_b64],
            "stream": False,
        }
        res = requests.post(url, json=payload, timeout=120)
        return res.json().get("response", "Could not analyze image.")
    except Exception as e:
        return f"Vision Error: {e}"


def query_ollama_video(video_path: str, prompt: str) -> str:
    import base64

    import cv2

    try:
        cap = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if total_frames <= 0:
            return "Could not read video."

        num_samples = 8
        step = max(total_frames // num_samples, 1)

        images_b64 = []
        for i in range(0, total_frames, step):
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frame = cap.read()
            if ret:
                # Resize frame to save memory
                frame = cv2.resize(frame, (512, 512))
                # Convert to jpg then base64
                _, buffer = cv2.imencode(".jpg", frame)
                img_b64 = base64.b64encode(buffer).decode("utf-8")
                images_b64.append(img_b64)
                if len(images_b64) >= num_samples:
                    break
        cap.release()

        url = "http://localhost:11434/api/generate"
        payload = {
            "model": "qwen2.5vl:7b",
            "prompt": prompt,
            "images": images_b64,
            "stream": False,
        }
        res = requests.post(url, json=payload, timeout=300)
        return res.json().get("response", "Could not analyze video.")
    except Exception as e:
        return f"Video Vision Error: {e}"


def process_message(chat_id: int, text: str):
    text_clean = text.strip()
    lower_text = text_clean.lower()

    if text_clean == "/start":
        msg = "👋 *Hello! I am your Antigravity Enterprise AI Security & Control Hub.*\n\nI am running 100% locally on your PC! Use the touch panel below or send any command."
        send_message(chat_id, msg, show_keyboard=True)
        return

    if text_clean in ["/help", "/panel", "/menu"]:
        msg = (
            "🛠 *Enterprise AI Control Center:*\n"
            "• Touch buttons below for instant room photos, video clips, and sentinel control.\n"
            "• Send natural language commands to the God-Tier AI Engine."
        )
        send_message(chat_id, msg, show_keyboard=True)
        return

    # Remote Room Footage & Live Snapshot Handlers
    room_photo_keywords = [
        "/room",
        "/camera",
        "show my room",
        "check my room",
        "room photo",
        "room camera",
        "take room picture",
        "live room photo",
        "room snapshot",
        "room footage",
        "access my room footage",
        "take a room photo",
    ]
    if any(k == lower_text or lower_text.startswith(k) for k in room_photo_keywords):
        send_message(chat_id, "📷 *Accessing live room camera...*")
        try:
            import cv2

            cap = (
                cv2.VideoCapture(0, cv2.CAP_DSHOW)
                if sys.platform.startswith("win")
                else cv2.VideoCapture(0)
            )
            if not cap.isOpened():
                try:
                    cap.release()
                except Exception:
                    pass
                cap = cv2.VideoCapture(0)

            try:
                if cap.isOpened():
                    ret, frame = cap.read()
                else:
                    ret, frame = False, None
            finally:
                try:
                    cap.release()
                except Exception:
                    pass

            if ret and frame is not None:
                if ret and frame is not None:
                    import uuid

                    temp_dir = os.path.abspath(
                        os.path.join(os.path.dirname(__file__), "temp_media")
                    )
                    os.makedirs(temp_dir, exist_ok=True)
                    snap_path = os.path.join(
                        temp_dir, f"remote_room_{uuid.uuid4().hex[:8]}.jpg"
                    )
                    cv2.imwrite(snap_path, frame)
                    caption = f"📷 *Live Room Snapshot (Remote Access)*"
                    send_photo(chat_id, snap_path, caption)
                    try:
                        if os.path.exists(snap_path):
                            os.remove(snap_path)
                    except Exception:
                        pass
                    return
                else:
                    send_message(
                        chat_id, "⚠️ Could not capture frame from room camera."
                    )
                    return
            else:
                send_message(
                    chat_id, "⚠️ Room camera is currently disconnected or busy."
                )
                return
        except Exception as e:
            send_message(chat_id, f"⚠️ Room camera error: {e}")
            return

    room_video_keywords = [
        "/roomvideo",
        "/clip",
        "send room video",
        "room video",
        "record room",
        "live room video",
        "room clip",
        "take a room video",
    ]
    if any(k == lower_text or lower_text.startswith(k) for k in room_video_keywords):
        send_message(chat_id, "🎥 *Recording 5-second live room video clip...*")
        try:
            import cv2

            cap = (
                cv2.VideoCapture(0, cv2.CAP_DSHOW)
                if sys.platform.startswith("win")
                else cv2.VideoCapture(0)
            )
            if not cap.isOpened():
                try:
                    cap.release()
                except Exception:
                    pass
                cap = cv2.VideoCapture(0)

            if cap.isOpened():
                import uuid

                temp_dir = os.path.abspath(
                    os.path.join(os.path.dirname(__file__), "temp_media")
                )
                os.makedirs(temp_dir, exist_ok=True)
                vid_clip_path = os.path.join(
                    temp_dir, f"remote_clip_{uuid.uuid4().hex[:8]}.mp4"
                )

                fourcc = cv2.VideoWriter_fourcc(*"mp4v")
                fps = 15
                out = cv2.VideoWriter(vid_clip_path, fourcc, fps, (640, 480))

                start_rec = time.time()
                try:
                    while (time.time() - start_rec) < 5.0:
                        ret, f = cap.read()
                        if ret and f is not None:
                            resized_f = cv2.resize(f, (640, 480))
                            out.write(resized_f)
                        time.sleep(1.0 / fps)
                finally:
                    try:
                        out.release()
                    except Exception:
                        pass
                    try:
                        cap.release()
                    except Exception:
                        pass

                send_video(chat_id, vid_clip_path, "🎥 *5-Second Live Room Video Clip*")
                try:
                    if os.path.exists(vid_clip_path):
                        os.remove(vid_clip_path)
                except Exception:
                    pass
                return
            else:
                send_message(chat_id, "⚠️ Room camera is disconnected or busy.")
                return
        except Exception as e:
            send_message(chat_id, f"⚠️ Room video recording error: {e}")
            return

    # TP-Link Kasa Smart Light Control
    if any(
        w in lower_text
        for w in [
            "light",
            "kasa",
            "tp link",
            "tplink",
            "room light",
            "turn off room ligh",
            "turn on room ligh",
        ]
    ):
        try:
            import kasa_controller

            kasa_res = kasa_controller.execute_kasa_intent(text_clean)
            if kasa_res:
                kasa_msg, _ = kasa_res
                send_message(chat_id, kasa_msg)
                return
        except Exception as e:
            send_message(chat_id, f"⚠️ Smart light error: {e}")

    print(
        f"[{time.strftime('%H:%M:%S')}] Processing intent via Autonomous Engine: {text_clean}"
    )
    send_message(chat_id, "🔄 *Processing intent...*")

    try:
        # Route to the main autonomous intent engine!
        res = autonomous_intent_engine.handle_autonomous_intent(text_clean)

        if res:
            response_text = res[0]

            if response_text:
                send_message(chat_id, response_text)
            else:
                send_message(chat_id, "✅ *Action executed successfully.*")
        else:
            try:
                import requests

                send_message(chat_id, "🧠 *Routing to Skills API...*")

                # Check if it starts with a skill command (e.g. /python-pro)
                payload = {"skill_name": "general", "prompt": text_clean}
                if text_clean.startswith("/"):
                    parts = text_clean.split(" ", 1)
                    if len(parts) > 1:
                        payload["skill_name"] = parts[0][1:]
                        payload["prompt"] = parts[1]
                    else:
                        payload["skill_name"] = parts[0][1:]
                        payload["prompt"] = ""

                api_url = "http://localhost:8000/api/execute_skill"
                res_api = requests.post(api_url, json=payload, timeout=600)

                if res_api.status_code == 200:
                    ai_reply = res_api.json().get(
                        "result", "Skill executed, but returned nothing."
                    )
                    send_message(chat_id, ai_reply)
                else:
                    send_message(chat_id, f"⚠️ Skills API Error: {res_api.text}")
            except requests.exceptions.ConnectionError:
                send_message(
                    chat_id,
                    "❌ Could not connect to Skills API (is `skills_api.py` running on port 8000?)",
                )
            except Exception as e:
                send_message(chat_id, f"⚠️ Error: {e}")

    except Exception as e:
        err_msg = f"⚠️ *Critical Engine Error:* {e}"
        print(f"[TelegramService] Engine Error: {traceback.format_exc()}")
        send_message(chat_id, err_msg)


def run_telegram_polling():
    """Main polling loop for receiving Telegram updates."""
    print("==================================================")
    print("[+] Antigravity Telegram AI Service is ONLINE!")
    print("[+] Engine: Autonomous Intent Engine")
    print("==================================================")

    offset = 0
    while True:
        try:
            url = f"{BASE_URL}/getUpdates"
            params = {"offset": offset, "timeout": 30}
            response = requests.get(url, params=params, timeout=35)

            if response.status_code == 200:
                data = response.json()
                for update in data.get("result", []):
                    offset = update["update_id"] + 1
                    message = update.get("message")

                    if message:
                        chat_id = message["chat"]["id"]

                        if "text" in message:
                            user_text = message["text"]
                            print(
                                f"[{time.strftime('%H:%M:%S')}] Received text from {chat_id}: {user_text}"
                            )
                            process_message(chat_id, user_text)

                        elif "voice" in message or "audio" in message:
                            media_obj = message.get("voice") or message.get("audio")
                            file_id = media_obj["file_id"]
                            print(
                                f"[{time.strftime('%H:%M:%S')}] Received audio from {chat_id}"
                            )
                            send_message(
                                chat_id,
                                "🎙️ *Downloading and transcribing voice note...*",
                            )
                            local_path = download_telegram_file(file_id, ".ogg")
                            if local_path:
                                try:
                                    from faster_whisper import WhisperModel

                                    model = WhisperModel(
                                        "small", device="cuda", compute_type="float16"
                                    )
                                    segments, _ = model.transcribe(
                                        local_path, beam_size=5
                                    )
                                    text = " ".join(
                                        [segment.text for segment in segments]
                                    ).strip()
                                    send_message(
                                        chat_id, f"🗣️ *Transcribed Command:*\n_{text}_"
                                    )
                                    if text:
                                        process_message(chat_id, text)
                                except Exception as e:
                                    send_message(
                                        chat_id, f"⚠️ Error transcribing audio: {e}"
                                    )
                                finally:
                                    if os.path.exists(local_path):
                                        os.remove(local_path)

                        elif (
                            "photo" in message
                            or "video" in message
                            or "video_note" in message
                        ):
                            print(
                                f"[{time.strftime('%H:%M:%S')}] Received visual media from {chat_id}"
                            )
                            send_message(
                                chat_id, "👁️ *Analyzing visual media with Vision AI...*"
                            )

                            is_video = "video" in message or "video_note" in message
                            if is_video:
                                media_obj = message.get("video") or message.get(
                                    "video_note"
                                )
                                suffix = ".mp4"
                            else:
                                media_obj = message["photo"][-1]
                                suffix = ".jpg"

                            file_id = media_obj["file_id"]
                            local_path = download_telegram_file(file_id, suffix)

                            if local_path:
                                if is_video:
                                    try:
                                        vision_text = query_ollama_video(
                                            local_path,
                                            "Describe the events in this video in detail.",
                                        )
                                        send_message(
                                            chat_id,
                                            f"👁️ *Full Video Analysis:*\n{vision_text}",
                                        )
                                    except Exception as e:
                                        send_message(
                                            chat_id, f"⚠️ Video processing error: {e}"
                                        )
                                else:
                                    vision_text = query_ollama_vision(
                                        local_path, "Describe this image in detail."
                                    )
                                    send_message(
                                        chat_id, f"👁️ *Image Analysis:*\n{vision_text}"
                                    )

                                if os.path.exists(local_path):
                                    os.remove(local_path)

                    elif "callback_query" in update:
                        cb = update["callback_query"]
                        cb_id = cb["id"]
                        cb_data = cb.get("data", "")
                        cb_chat_id = cb["message"]["chat"]["id"]
                        print(
                            f"[{time.strftime('%H:%M:%S')}] Button tapped: {cb_data} from {cb_chat_id}"
                        )
                        answer_callback_query(cb_id, "Processing command...")

                        if cb_data == "cmd_room_photo":
                            process_message(cb_chat_id, "take a room photo")
                        elif cb_data == "cmd_room_video":
                            process_message(cb_chat_id, "take a room video")
                        elif cb_data == "cmd_sentinel_on":
                            process_message(cb_chat_id, "turn on sentinel")
                        elif cb_data == "cmd_sentinel_off":
                            process_message(cb_chat_id, "turn off sentinel")
                        elif cb_data == "cmd_system_health":
                            process_message(cb_chat_id, "system health")
                        elif cb_data == "cmd_daily_report":
                            process_message(cb_chat_id, "daily report")

            else:
                print(
                    f"[{time.strftime('%H:%M:%S')}] Telegram polling HTTP {response.status_code}: backing off 5s..."
                )
                time.sleep(5)

        except requests.exceptions.RequestException as e:
            print(f"[TelegramService] Network polling retry: {e}")
            time.sleep(3)
        except Exception as e:
            print(f"[TelegramService] Polling exception: {e}\n{traceback.format_exc()}")
            time.sleep(3)


if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    run_telegram_polling()
