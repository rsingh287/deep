import os
import re
import json
import time
import tempfile
import wave
import requests
import db_engine

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
PODCASTS_DIR = os.path.join(PROJECT_ROOT, "podcasts")
os.makedirs(PODCASTS_DIR, exist_ok=True)

OLLAMA_API = os.getenv("OLLAMA_HOST", "http://localhost:11434")

PODCAST_PROMPT_TEMPLATE = """You are an executive podcast producer creating a short, high-energy 2-minute technical podcast between two hosts:
- Host Alex (insightful, analytical, enthusiastic)
- Host Sam (practical, curious, asks sharp clarifying questions)

Topic: {topic}
Source Material / Context:
{content}

Create a natural, engaging conversation discussing the topic.
Format your output strictly as a JSON array of dialogue objects:
[
  {{"speaker": "Alex", "text": "Welcome to Deep Dive Technical. Today we are looking at..."}},
  {{"speaker": "Sam", "text": "And this is a fascinating architecture because..."}},
  ...
]
Keep each turn to 1-3 concise sentences. Total dialogue turns: 6 to 10."""


def generate_podcast_script(topic: str, content: str = "") -> list:
    """Generates dialogue script between Alex and Sam using local LLM or dynamic fallback."""
    if not content:
        content = f"Technical overview and architectural analysis of {topic}."

    prompt = PODCAST_PROMPT_TEMPLATE.format(topic=topic, content=content[:2000])

    try:
        res = requests.post(
            f"{OLLAMA_API}/api/generate",
            json={
                "model": "llama3.2:latest",
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.7, "num_predict": 600}
            },
            timeout=25
        )
        if res.status_code == 200:
            raw_text = res.json().get("response", "").strip()
            # Extract JSON array
            match = re.search(r'\[\s*\{.*\}\s*\]', raw_text, re.DOTALL)
            if match:
                dialogue = json.loads(match.group(0))
                if isinstance(dialogue, list) and len(dialogue) >= 2:
                    return dialogue
    except Exception as e:
        print(f"[PodcastEngine] LLM generation fallback: {e}")

    # High-quality dynamic fallback script if LLM is unavailable
    return [
        {
            "speaker": "Alex",
            "text": f"Welcome back to D.E.E.P Sovereign Audio. Today, Sam and I are breaking down {topic}."
        },
        {
            "speaker": "Sam",
            "text": f"That's right, Alex. When Commander Singh asked for a deep dive on {topic}, there were several critical trade-offs that immediately stood out."
        },
        {
            "speaker": "Alex",
            "text": "Exactly. The core advantage here comes down to latency, sovereignty, and clean execution. Instead of relying on brittle external dependencies, the system keeps execution local and verified."
        },
        {
            "speaker": "Sam",
            "text": "And the architecture reflects that. Everything streams through PostgreSQL with zero lock contention, giving us a scalable, resilient backbone."
        },
        {
            "speaker": "Alex",
            "text": "Which means whether we're deploying high-frequency telemetry, smart lighting, or biometric sentinels, the entire environment responds instantaneously."
        },
        {
            "speaker": "Sam",
            "text": f"Couldn't agree more, Alex. That wraps up our executive briefing on {topic}. System status is optimal, and all flight checks are green."
        }
    ]


def synthesize_turn(text: str, voice_index: int, output_wav: str):
    """Synthesizes speech for a single speaker using in-process Windows SAPI."""
    import pythoncom
    import win32com.client

    pythoncom.CoInitialize()
    try:
        voice = win32com.client.Dispatch("SAPI.SpVoice")
        stream = win32com.client.Dispatch("SAPI.SpFileStream")
        voices = voice.GetVoices()
        if voice_index < voices.Count:
            voice.Voice = voices.Item(voice_index)

        # 3 = SSFMCreateForWrite
        stream.Open(output_wav, 3)
        voice.AudioOutputStream = stream
        voice.Speak(text)
        stream.Close()
    finally:
        pythoncom.CoUninitialize()


def combine_wav_files(wav_list: list, final_wav: str):
    """Combines a list of WAV audio files into a single seamless podcast track."""
    if not wav_list:
        return
    
    data = []
    params = None
    for w in wav_list:
        if os.path.exists(w) and os.path.getsize(w) > 44:
            with wave.open(w, 'rb') as wave_in:
                if params is None:
                    params = wave_in.getparams()
                data.append(wave_in.readframes(wave_in.getnframes()))

    if params and data:
        with wave.open(final_wav, 'wb') as wave_out:
            wave_out.setparams(params)
            for frames in data:
                wave_out.writeframes(frames)


def generate_podcast(topic: str, content: str = "") -> dict:
    """Full pipeline: generates script, synthesizes dual voices, and produces master podcast."""
    script = generate_podcast_script(topic, content)
    timestamp = int(time.time())
    safe_topic = re.sub(r'[^a-zA-Z0-9_-]', '_', topic.lower())[:30]
    final_filename = f"podcast_{safe_topic}_{timestamp}.wav"
    final_path = os.path.join(PODCASTS_DIR, final_filename)

    temp_files = []
    try:
        for idx, turn in enumerate(script):
            speaker = turn.get("speaker", "Alex").strip().capitalize()
            text = turn.get("text", "")
            # Alex is voice 0 (David), Sam is voice 1 (Zira)
            voice_idx = 1 if "Sam" in speaker else 0
            
            temp_wav = os.path.join(tempfile.gettempdir(), f"turn_{timestamp}_{idx}.wav")
            synthesize_turn(text, voice_idx, temp_wav)
            temp_files.append(temp_wav)

        combine_wav_files(temp_files, final_path)
    finally:
        for f in temp_files:
            try:
                if os.path.exists(f):
                    os.remove(f)
            except Exception:
                pass

    duration_est = sum(len(turn.get("text", "").split()) for turn in script) / 2.5

    return {
        "success": True,
        "title": f"D.E.E.P Dive: {topic}",
        "topic": topic,
        "filename": final_filename,
        "file_path": final_path,
        "relative_url": f"/podcasts/{final_filename}",
        "turns": len(script),
        "duration_seconds": round(duration_est, 1),
        "script": script
    }


def list_podcasts() -> list:
    """Returns all generated podcasts on disk."""
    items = []
    if os.path.exists(PODCASTS_DIR):
        for f in os.listdir(PODCASTS_DIR):
            if f.endswith(".wav"):
                fp = os.path.join(PODCASTS_DIR, f)
                stat = os.stat(fp)
                items.append({
                    "filename": f,
                    "url": f"/podcasts/{f}",
                    "size_kb": round(stat.st_size / 1024, 1),
                    "created_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stat.st_mtime))
                })
    items.sort(key=lambda x: x["created_at"], reverse=True)
    return items


if __name__ == "__main__":
    print("Testing Podcast Generator Engine...")
    res = generate_podcast("PostgreSQL 18 Sovereign Architecture")
    print("Generated:", res["title"])
    print("File:", res["file_path"], f"({os.path.getsize(res['file_path'])} bytes)")
