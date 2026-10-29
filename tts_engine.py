import base64
import os
import re
import subprocess
import tempfile
from typing import Any, Dict


def clean_speech_text(text: str, max_chars: int = 1500) -> str:
    """Strips markdown, emojis, HTML tags, and code blocks for clean TTS pronunciation."""
    if not text:
        return ""

    # Remove code blocks
    cleaned = re.sub(r"```[\s\S]*?```", " Code block generated. ", text)
    cleaned = re.sub(r"`[^`]*`", "", cleaned)
    # Remove markdown links [title](url) -> title
    cleaned = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", cleaned)
    # Remove URLs
    cleaned = re.sub(r"https?://\S+", "", cleaned)
    # Remove HTML tags
    cleaned = re.sub(r"<[^>]+>", "", cleaned)
    # Remove special symbols
    cleaned = re.sub(r"[*_#~|]", "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    if len(cleaned) > max_chars:
        cut = cleaned[:max_chars]
        last_punct = max(
            cut.rfind(". "), cut.rfind("! "), cut.rfind("? "), cut.rfind("; ")
        )
        if last_punct > max_chars // 2:
            cleaned = cut[: last_punct + 1]
        else:
            cleaned = cut

    return cleaned


def text_to_speech_in_process_sapi(text: str) -> str:
    """
    Ultra-fast in-process Windows SAPI synthesis using win32com (~50ms latency).
    Returns base64-encoded WAV data.
    """
    try:
        import pythoncom
        import win32com.client

        pythoncom.CoInitialize()
        voice = win32com.client.Dispatch("SAPI.SpVoice")
        stream = win32com.client.Dispatch("SAPI.SpFileStream")

        temp_wav = os.path.join(
            tempfile.gettempdir(), f"deep_tts_{os.getpid()}_{id(text)}.wav"
        )
        # 3 = SSFMCreateForWrite (create or overwrite)
        stream.Open(temp_wav, 3)
        voice.AudioOutputStream = stream
        voice.Speak(text)
        stream.Close()
        pythoncom.CoUninitialize()

        if os.path.exists(temp_wav) and os.path.getsize(temp_wav) > 0:
            with open(temp_wav, "rb") as f:
                b64_audio = base64.b64encode(f.read()).decode("utf-8")
            try:
                os.remove(temp_wav)
            except Exception:
                pass
            return b64_audio
    except Exception as e:
        print(
            f"[TTS] win32com in-process SAPI error: {e}, falling back to PowerShell..."
        )
    return ""


def text_to_speech_powershell_fallback(text: str) -> str:
    """Fallback using PowerShell System.Speech.Synthesis."""
    cleaned_text = text.replace('"', '"').replace("\n", " ").replace("'", "'")
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        wav_path = f.name.replace("\\", "/")

    ps_script = f"""
Add-Type -AssemblyName System.speech;
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer;
$synth.SetOutputToWaveFile('{wav_path}');
$synth.Speak("{cleaned_text}");
$synth.Dispose();
"""
    try:
        res = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_script],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if os.path.exists(wav_path) and os.path.getsize(wav_path) > 0:
            with open(wav_path, "rb") as audio_file:
                b64_audio = base64.b64encode(audio_file.read()).decode("utf-8")
            try:
                os.remove(wav_path)
            except Exception:
                pass
            return b64_audio
    except Exception as e:
        print(f"[TTS] PowerShell synthesis error: {e}")
    finally:
        if os.path.exists(wav_path):
            try:
                os.remove(wav_path)
            except Exception:
                pass
    return ""


def speak_offline(text: str) -> Dict[str, Any]:
    """Generates offline TTS audio response with <100ms latency."""
    try:
        import voice_state
        if voice_state.is_voice_muted():
            return {"status": "muted", "audio_b64": "", "message": "Voice is muted by user."}
    except Exception:
        pass

    clean_text = clean_speech_text(text)
    if not clean_text:
        return {"status": "error", "message": "No valid text to speak."}

    # 1. Try ultra-fast in-process SAPI
    b64_wav = text_to_speech_in_process_sapi(clean_text)

    # 2. Fallback to PowerShell SAPI
    if not b64_wav:
        b64_wav = text_to_speech_powershell_fallback(clean_text)

    if b64_wav:
        return {
            "status": "success",
            "audio_b64": b64_wav,
            "format": "audio/wav",
            "text": clean_text,
        }
    return {"status": "error", "message": "Failed to synthesize speech offline."}


def synthesize_to_base64_wav(text: str) -> str:
    """Synthesizes text into base64-encoded WAV audio string."""
    res = speak_offline(text)
    if isinstance(res, dict) and res.get("status") == "success":
        return res.get("audio_b64", "")
    return ""
