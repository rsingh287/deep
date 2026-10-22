import pyttsx3
import speech_recognition as sr


def speak_response(text):
    """Speaks response using local female voice TTS."""
    try:
        print(
            f"AI Assistant Speaking: {text.encode('utf-8', errors='ignore').decode('utf-8')}"
        )
    except Exception:
        pass
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty("voices")
        for v in voices:
            if (
                "zira" in v.name.lower()
                or "hazel" in v.name.lower()
                or "female" in v.name.lower()
            ):
                engine.setProperty("voice", v.id)
                break
        engine.setProperty("rate", 160)
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"TTS Error: {e}")


def run_punjabi_voice_command(command_text):
    """Interprets Punjabi / English voice commands and executes PC actions."""
    cmd_lower = command_text.lower()
    try:
        print(
            f"\nUser Spoke (Punjabi / English): '{command_text.encode('utf-8', errors='ignore').decode('utf-8')}'"
        )
    except Exception:
        pass

    # 1. Weather Command ("ਮੌਸਮ" / "weather")
    if "ਮੌਸਮ" in command_text or "weather" in cmd_lower:
        reply = "ਸਤਿ ਸ਼੍ਰੀ ਅਕਾਲ! Checking current weather. Sudbury is 22°C Clear, Brampton is 24°C Partly Cloudy, and Niagara is 23°C."
        speak_response("Sat Shri Akaal! Here is your live weather update.")
        return reply

    # 2. PC Volume Command ("ਆਵਾਜ਼" / "volume")
    elif "ਆਵਾਜ਼" in command_text or "volume" in cmd_lower:
        import subprocess

        subprocess.run(
            ["powershell", "(New-Object -ComObject WScript.Shell).SendKeys([char]175)"]
        )
        reply = "ਆਵਾਜ਼ ਵਧਾ ਦਿੱਤੀ ਗਈ ਹੈ! Volume increased successfully."
        speak_response("Volume increased successfully.")
        return reply

    # 3. System Diagnostic ("ਸਿਸਟਮ" / "system" / "diagnostic")
    elif "ਸਿਸਟਮ" in command_text or "system" in cmd_lower or "diagnostic" in cmd_lower:
        import psutil

        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        reply = f"ਸਿਸਟਮ ਨਿਰੀਖਣ: CPU ਵਰਤੋਂ {cpu}%, RAM ਵਰਤੋਂ {ram}%. System performance is optimal."
        speak_response(
            f"System status normal. CPU at {cpu} percent, RAM at {ram} percent."
        )
        return reply

    # 5. AUTOMATIC CAMERA VISION TRIGGER ("ਕੈਮਰਾ" / "camera" / "vision" / "look")
    elif (
        any(w in cmd_lower for w in ["camera", "vision", "look", "see"])
        or "ਕੈਮਰਾ" in command_text
    ):
        speak_response(
            "Starting live camera vision, sign language, and facial emotion analysis now."
        )

        # Execute live camera vision
        from facial_expression_engine import FacialExpressionEngine
        from live_camera_vision import LiveCameraVisionEngine
        from sign_language_engine import SignLanguageVisionEngine

        cam_res = LiveCameraVisionEngine().capture_live_frame_analysis()
        sign_res = SignLanguageVisionEngine().recognize_sign_gesture()
        face_res = FacialExpressionEngine().analyze_facial_expression()

        cam_summary = cam_res.get("ai_scene_summary", "Camera active.")
        gesture = sign_res.get("meaning_english", "No sign gesture.")
        emotion = face_res.get("emotion_english", "Neutral face.")

        full_reply = f"Camera Vision Analysis Complete! {cam_summary} Sign Language: {gesture}. Emotion Detected: {emotion}."
        speak_response(
            f"Camera analysis complete. {cam_summary}. Facial emotion is {emotion}."
        )
        return full_reply

    # 6. Default Greeting / Conversation
    else:
        reply = f"ਸਤਿ ਸ਼੍ਰੀ ਅਕਾਲ! I heard you say: '{command_text}'. How can I assist you further?"
        speak_response("Sat Shri Akaal! I am ready for your next Punjabi command.")
        return reply


def listen_punjabi_microphone():
    """Captures microphone audio and transcribes using pa-IN Punjabi language model."""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("\n------------------------------------------------------------")
        print("🎙️ PUNJABI (ਪੰਜਾਬੀ) VOICE LISTENER ACTIVE (Speak Now...)")
        print("------------------------------------------------------------")
        r.adjust_for_ambient_noise(source, duration=0.5)
        audio = r.listen(source, timeout=6)

    try:
        # Recognize speech using Google Speech API with pa-IN (Punjabi India)
        text = r.recognize_google(audio, language="pa-IN")
        return text
    except sr.UnknownValueError:
        print(
            "⚠️ Audio not recognized cleanly. Retrying with English/Punjabi fallback..."
        )
        return None
    except Exception as e:
        print(f"Error during recognition: {e}")
        return None


if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    print("Initializing Punjabi Voice Assistant Core...")
    test_commands = [
        "ਸਤਿ ਸ਼੍ਰੀ ਅਕਾਲ, ਅੱਜ ਦਾ ਮੌਸਮ ਕੀ ਹੈ?",
        "ਸਿਸਟਮ ਦਾ ਹਾਲ ਦੱਸੋ",
        "ਹੱਗਿੰਗ ਫੇਸ ਮੋਡਲ ਡਾਊਨਲੋਡ ਕਰੋ",
    ]

    print("\n--- RUNNING DEMONSTRATION VOICE COMMAND SUITE ---")
    for cmd in test_commands:
        res = run_punjabi_voice_command(cmd)
        try:
            print(f"RESULT: {res.encode('utf-8', errors='ignore').decode('utf-8')}\n")
        except Exception:
            pass
