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


# =====================================================================
# PIC18F85K22 & PICkit 3 Hardware Endpoints (Deep AI Coprocessor Bridge)
# =====================================================================

@hardware_bp.route("/api/pic/status", methods=["GET"])
def get_pic_status():
    try:
        import pic_embedded_engine
        detection = pic_embedded_engine.detect_pickit3()
        specs = pic_embedded_engine.get_board_specs()
        return jsonify({
            "success": True,
            "pickit3": detection,
            "board_specs": specs
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@hardware_bp.route("/api/pic/projects", methods=["GET"])
def get_pic_projects():
    try:
        import pic_embedded_engine
        projects = pic_embedded_engine.list_workspace_projects()
        return jsonify({"success": True, "projects": projects})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@hardware_bp.route("/api/pic/compile", methods=["POST"])
def compile_pic_project():
    try:
        from flask import request
        import pic_embedded_engine

        data = request.json or {}
        project = data.get("project")
        if not project:
            return jsonify({"success": False, "error": "Missing 'project' parameter"}), 400

        result = pic_embedded_engine.compile_project(project)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@hardware_bp.route("/api/pic/flash", methods=["POST"])
def flash_pic_project():
    try:
        from flask import request
        import pic_embedded_engine

        data = request.json or {}
        hex_path = data.get("hex_path")
        project = data.get("project")

        if not hex_path and project:
            p_dir = project if project.endswith(".X") else f"{project}.X"
            hex_path = os.path.join(pic_embedded_engine.PROJECTS_DIR, p_dir, "dist", "default", "production", f"{p_dir}.production.hex")

        if not hex_path:
            return jsonify({"success": False, "error": "Missing 'hex_path' or 'project' parameter"}), 400

        result = pic_embedded_engine.flash_firmware(hex_path)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@hardware_bp.route("/api/pic/audit", methods=["POST"])
def audit_pic_code():
    try:
        from flask import request
        import pic_embedded_engine

        data = request.json or {}
        code = data.get("code", "")
        result = pic_embedded_engine.audit_c_code(code)
        return jsonify({"success": True, "audit": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@hardware_bp.route("/api/pic/scaffold", methods=["POST"])
def scaffold_pic_project():
    try:
        from flask import request
        import pic_embedded_engine

        data = request.json or {}
        project = data.get("project", "pic_demo")
        code = data.get("code", "")
        if not code:
            return jsonify({"success": False, "error": "Missing 'code' parameter"}), 400

        result = pic_embedded_engine.scaffold_and_compile_project(project, code)
        return jsonify({"success": True, "result": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})





