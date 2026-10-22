from flask import Blueprint, jsonify
import psutil
import subprocess

hardware_bp = Blueprint('hardware', __name__)

@hardware_bp.route("/api/hardware/status", methods=["GET"])
def get_hardware_status():
    try:
        cpu = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory()
        
        # Try to get GPU stats
        gpu_info = "N/A"
        try:
            res = subprocess.run(["nvidia-smi", "--query-gpu=temperature.gpu,memory.used,memory.total", "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=2)
            if res.returncode == 0 and res.stdout.strip():
                parts = res.stdout.strip().split(',')
                if len(parts) >= 3:
                    gpu_info = f"Temp: {parts[0].strip()}°C | VRAM: {parts[1].strip()}/{parts[2].strip()} MB"
        except Exception:
            pass
            
        return jsonify({
            "success": True,
            "cpu_percent": cpu,
            "ram_percent": mem.percent,
            "gpu": gpu_info
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@hardware_bp.route("/api/kasa/status", methods=["GET"])
def get_kasa_status():
    try:
        import kasa_chroma_sync
        scenes = kasa_chroma_sync.get_available_scenes()
        return jsonify({
            "success": True,
            "connected": True,
            "active_scene": "voice_active",
            "available_scenes": scenes
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@hardware_bp.route("/api/media/control", methods=["POST"])
def control_media():
    try:
        from flask import request
        import local_music_engine

        data = request.json or {}
        action = data.get("action", "play_pause")
        res = local_music_engine.control_media(action)
        status = local_music_engine.get_media_status()
        return jsonify({"success": True, "action": action, "result": res, "status": status})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@hardware_bp.route("/api/media/status", methods=["GET"])
def get_media_status():
    try:
        import local_music_engine
        status = local_music_engine.get_media_status()
        return jsonify({"success": True, "status": status})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})








