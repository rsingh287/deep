import os
import numpy as np

# --- Kokoro ONNX (high-quality, requires model download) ---
try:
    from kokoro_onnx import Kokoro
    import sounddevice as sd
    _KOKORO_AVAILABLE = True
except ImportError:
    Kokoro = None
    sd = None
    _KOKORO_AVAILABLE = False

# --- pyttsx3 (offline fallback, zero dependencies) ---
try:
    import pyttsx3
    _PYTTSX3_AVAILABLE = True
except ImportError:
    pyttsx3 = None
    _PYTTSX3_AVAILABLE = False

_KOKORO_MODEL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kokoro-v0_19.onnx")
_KOKORO_VOICES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "voices.bin")


class DEEPOmniVoice:
    def __init__(self):
        self.kokoro = None
        self._pyttsx3_engine = None
        self.active = False
        self.backend = "none"

        # Try Kokoro first (best quality, neural TTS)
        if _KOKORO_AVAILABLE and os.path.isfile(_KOKORO_MODEL) and os.path.isfile(_KOKORO_VOICES):
            print("[OmniVoice] Initializing Kokoro-ONNX neural voice synthesis...")
            try:
                self.kokoro = Kokoro(_KOKORO_MODEL, _KOKORO_VOICES)
                self.active = True
                self.backend = "kokoro"
                print("[OmniVoice] Kokoro neural TTS engine ONLINE.")
                return
            except Exception as e:
                print(f"[OmniVoice] Kokoro load failed: {e}")

        # Fallback to pyttsx3 (works fully offline, no model downloads)
        if _PYTTSX3_AVAILABLE:
            print("[OmniVoice] Falling back to pyttsx3 offline TTS.")
            try:
                self._pyttsx3_engine = pyttsx3.init()
                self._pyttsx3_engine.setProperty("rate", 185)
                self._pyttsx3_engine.setProperty("volume", 1.0)
                self.active = True
                self.backend = "pyttsx3"
                print("[OmniVoice] pyttsx3 TTS engine ONLINE (offline mode).")
                return
            except Exception as e:
                print(f"[OmniVoice] pyttsx3 init failed: {e}")

        print("[OmniVoice] No TTS backend available. Voice synthesis disabled.")

    def speak(self, text, voice="bm_george"):
        if not self.active:
            print("[OmniVoice] Voice system inactive or missing dependencies.")
            return

        try:
            import voice_state
            if voice_state.is_voice_muted():
                print(f"[OmniVoice] Voice is OFF (muted globally). Suppressing speech: '{text[:50]}...'")
                return
        except Exception:
            pass

        print(f"[OmniVoice] Synthesizing: '{text[:50]}...'")
        try:
            if self.backend == "kokoro":
                available = self.kokoro.get_voices() if hasattr(self.kokoro, 'get_voices') else []
                target_voice = voice if voice in available else ("bm_george" if "bm_george" in available else available[0])
                samples, sample_rate = self.kokoro.create(text, voice=target_voice, speed=1.0, lang="en-us")
                sd.play(samples, sample_rate)
                sd.wait()
            elif self.backend == "pyttsx3":
                self._pyttsx3_engine.say(text)
                self._pyttsx3_engine.runAndWait()
        except Exception as e:
            print(f"[OmniVoice] Playback error: {e}")

omni_voice_engine = None

def get_voice_engine():
    global omni_voice_engine
    if omni_voice_engine is None:
        omni_voice_engine = DEEPOmniVoice()
    return omni_voice_engine
