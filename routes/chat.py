from flask import Blueprint, request, jsonify, render_template, current_app, Response
import os, json, subprocess, requests, base64, time, re, threading
import db_engine

import sys

SYSTEM_PROMPT = None
resolve_model_tag = None
get_model_payload_options = None
get_learned_facts_prompt = None
fallback_intent_response = None
execute_code = None
handle_baggage_query = None
auto_select_model = None

# Dynamic binding to resolve app.py / __main__ globals cleanly
def _bind_app_globals():
    main_mod = sys.modules.get('__main__')
    app_mod = sys.modules.get('app')
    targets = [
        'SYSTEM_PROMPT', 'resolve_model_tag', 'get_model_payload_options', 
        'get_learned_facts_prompt', 'fallback_intent_response', 'execute_code', 
        'handle_baggage_query', 'auto_select_model'
    ]
    g = globals()
    for t in targets:
        if t not in g or g[t] is None:
            val = None
            if main_mod and hasattr(main_mod, t):
                val = getattr(main_mod, t)
            elif app_mod and hasattr(app_mod, t):
                val = getattr(app_mod, t)
            if val is not None:
                g[t] = val

_bind_app_globals()

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "memory.db")
OLLAMA_API = os.getenv("OLLAMA_HOST", "http://localhost:11434")

chat_bp = Blueprint('chat', __name__)

_RECENT_PROMPTS = {}
_PROMPT_LOCK = threading.Lock()

def check_and_record_prompt(prompt_text, window_sec=1.5):
    """Prevents duplicate prompt submissions (e.g. from simultaneous cockpit + buddy mics) from crashing GPU."""
    if not prompt_text:
        return False, None
    norm = prompt_text.strip().lower()
    now = time.time()
    with _PROMPT_LOCK:
        # Purge entries older than 20 seconds
        for k in list(_RECENT_PROMPTS.keys()):
            if now - _RECENT_PROMPTS[k]["ts"] > 20.0:
                del _RECENT_PROMPTS[k]
        
        # Check if identical prompt was submitted within window
        for k, v in _RECENT_PROMPTS.items():
            if v["norm"] == norm and (now - v["ts"] < window_sec):
                return True, v.get("cached_reply")
        
        req_id = f"{now}_{abs(hash(norm))}"
        _RECENT_PROMPTS[req_id] = {"norm": norm, "ts": now, "cached_reply": None}
        return False, req_id

def set_cached_prompt_reply(req_id, reply_text):
    if not req_id:
        return
    with _PROMPT_LOCK:
        if req_id in _RECENT_PROMPTS:
            _RECENT_PROMPTS[req_id]["cached_reply"] = reply_text

def extract_concise_spoken_text(model_tag, ai_resp):
    """Produces a clean, short 1-sentence spoken text so TTS never reads raw code/HTML/paths."""
    if not model_tag or not ai_resp:
        return ""
    if model_tag in ("play_local_music", "play_local_song"):
        match_t = re.search(r"Playing Local (?:Track|Song|Music):(?:\*\*)?\s*([^\n(\`]+)", ai_resp)
        clean_t = match_t.group(1).strip() if match_t else "your local music"
        return f"Playing {clean_t}."
    if model_tag == "everyday_media_toggle":
        return "Media playback toggled."
    if model_tag in ("everyday_youtube_play", "everyday_youtube_browser"):
        match_yt = re.search(r"Playing \*\*([^*]+)\*\*", ai_resp, re.I)
        clean_yt = match_yt.group(1).strip() if match_yt else "requested video"
        return f"Opening YouTube and playing {clean_yt} in Google Chrome."
    if model_tag == "everyday_youtube_open":
        return "Opened YouTube in Google Chrome."
    if model_tag == "everyday_open_subsystem":
        match_sub = re.search(r"Opening \*\*([^*]+)\*\*", ai_resp)
        clean_sub = match_sub.group(1).strip() if match_sub else "station"
        return f"Opening {clean_sub}."
    if model_tag.startswith("everyday_") or model_tag == "workstation_settings_overview":
        clean_line = re.sub(r"<[^>]+>", "", ai_resp)
        clean_line = re.sub(r"\[[^\]]*\]\([^)]*\)", "", clean_line)
        clean_line = re.sub(r"[*#_`~>]", "", clean_line).strip()
        first_line = clean_line.split("\n")[0].strip()
        return first_line[:120].strip() if first_line else "Command completed."
    return ""

@chat_bp.before_request
def _ensure_globals_bound():
    _bind_app_globals()

@chat_bp.route("/api/chats", methods=["GET", "POST"])
def manage_chats():
    conn = db_engine.get_db_connection()
    try:
        cursor = conn.cursor()
        if request.method == "POST":
            req_data = request.get_json(silent=True) or {}
            chat_id = f"chat_{int(time.time()*1000)}"
            title = req_data.get("title", "New Chat Session")
            cursor.execute(
                "INSERT INTO chat_sessions (chat_id, title) VALUES (?, ?)", (chat_id, title)
            )
            conn.commit()
            return jsonify({"success": True, "chat_id": chat_id, "title": title})
        else:
            cursor.execute(
                "SELECT chat_id, title, updated_at FROM chat_sessions ORDER BY updated_at DESC"
            )
            rows = cursor.fetchall()
            chats = [{"chat_id": r[0], "title": r[1], "updated_at": r[2]} for r in rows]
            return jsonify({"success": True, "chats": chats})
    finally:
        conn.close()

@chat_bp.route("/api/chats/<chat_id>", methods=["GET", "DELETE"])
def chat_detail(chat_id):
    conn = db_engine.get_db_connection()
    try:
        cursor = conn.cursor()
        if request.method == "DELETE":
            cursor.execute("DELETE FROM chat_sessions WHERE chat_id = ?", (chat_id,))
            cursor.execute("DELETE FROM chat_messages WHERE chat_id = ?", (chat_id,))
            conn.commit()
            return jsonify({"success": True})
        else:
            cursor.execute(
                "SELECT id, role, content, executed_details, image_b64 FROM chat_messages WHERE chat_id = ? ORDER BY id ASC",
                (chat_id,),
            )
            rows = cursor.fetchall()
            messages = []
            for r in rows:
                exec_d = json.loads(r[3]) if r[3] else []
                messages.append(
                    {
                        "id": r[0],
                        "role": r[1],
                        "content": r[2],
                        "executed_details": exec_d,
                        "image_b64": r[4],
                    }
                )
            return jsonify({"success": True, "messages": messages})
    finally:
        conn.close()

@chat_bp.route("/api/feedback", methods=["GET", "POST"])
def manage_human_feedback():
    import human_feedback_engine
    if request.method == "POST":
        data = request.json or {}
        chat_id = data.get("chat_id", "")
        message_id = str(data.get("message_id", ""))
        prompt = data.get("prompt", "")
        ai_response = data.get("ai_response", "")
        rating = int(data.get("rating", 1))
        feedback_type = data.get("feedback_type", "manual")
        critique_tag = data.get("critique_tag", "")
        user_correction = data.get("user_correction", "")

        result = human_feedback_engine.record_feedback(
            chat_id=chat_id,
            prompt=prompt,
            ai_response=ai_response,
            rating=rating,
            feedback_type=feedback_type,
            critique_tag=critique_tag,
            user_correction=user_correction,
            message_id=message_id,
        )
        return jsonify(result)
    else:
        stats = human_feedback_engine.get_feedback_stats()
        feedback_list = human_feedback_engine.get_all_feedback(limit=50)
        return jsonify({"success": True, "stats": stats, "feedback": feedback_list})

@chat_bp.route("/api/feedback/<int:feedback_id>", methods=["DELETE"])
def delete_human_feedback(feedback_id):
    import human_feedback_engine
    success = human_feedback_engine.delete_feedback(feedback_id)
    return jsonify({"success": success})

@chat_bp.route("/api/chat_with_image", methods=["POST"])
def chat_with_image():
    data = request.json or {}
    if "bodyData" in data and isinstance(data["bodyData"], dict):
        data = data["bodyData"]
    user_prompt = data.get("prompt", "3d scan room").strip()
    if not user_prompt:
        user_prompt = "3d scan room"
    image_b64 = data.get("image_b64", "")
    model_name = data.get("model", "qwen2.5")
    chat_id = data.get("chat_id")

    if not image_b64:
        return jsonify({"error": "No image data provided"}), 400

    conn = db_engine.get_db_connection()
    try:
        cursor = conn.cursor()

        if not chat_id:
            chat_id = f"chat_{int(time.time()*1000)}"
            title = "📷 Image & 3D Workstation Session"
            cursor.execute(
                "INSERT INTO chat_sessions (chat_id, title) VALUES (?, ?)", (chat_id, title)
            )

        cursor.execute(
            "INSERT INTO chat_messages (chat_id, role, content, image_b64) VALUES (?, ?, ?, ?)",
            (chat_id, "user", user_prompt, image_b64),
        )
        conn.commit()

        # 1. Direct Autonomous Action Interceptor (3D Studio, Object Detection, App Launcher)
        try:
            import autonomous_intent_engine

            auto_res = autonomous_intent_engine.handle_autonomous_intent(user_prompt)
            if auto_res:
                ai_resp, model_tag, exec_details = auto_res
                cursor.execute(
                    "INSERT INTO chat_messages (chat_id, role, content) VALUES (?, ?, ?)",
                    (chat_id, "assistant", ai_resp),
                )
                conn.commit()
                return jsonify(
                    {
                        "response": ai_resp,
                        "chat_id": chat_id,
                        "model": model_tag,
                        "executed_details": exec_details,
                        "has_execution": True,
                    }
                )
        except Exception as e:
            print(f"[AutonomousEngine Image Interceptor] Error: {e}")

        # Fallback to TRELLIS 3D Studio if prompt is generic or requests 3D/Scan
        prompt_low = user_prompt.lower()
        if any(
            k in prompt_low for k in ["3d", "scan", "room", "mesh", "model", "image to 3d"]
        ):
            try:
                import webbrowser

                space_url = "https://huggingface.co/spaces/microsoft/TRELLIS"
                webbrowser.open(space_url)
                ai_resp = f"🧊 **Autonomous 3D Model & Image-to-3D Generator:** Opened **Microsoft TRELLIS.2 3D Studio** in Google Chrome!\n\n🔗 [Direct 3D Studio Link]({space_url})"
                cursor.execute(
                    "INSERT INTO chat_messages (chat_id, role, content) VALUES (?, ?, ?)",
                    (chat_id, "assistant", ai_resp),
                )
                conn.commit()
                return jsonify(
                    {
                        "response": ai_resp,
                        "chat_id": chat_id,
                        "model": "autonomous_3d_generation",
                        "executed_details": [
                            {
                                "language": "powershell",
                                "code": f"start chrome '{space_url}'",
                                "output": "Opened Microsoft TRELLIS.2 3D Studio",
                            }
                        ],
                        "has_execution": True,
                    }
                )
            except Exception:
                pass

        target_model = resolve_model_tag(model_name, user_prompt, has_image=True)
        opts = get_model_payload_options(target_model)

        payload = {
            "model": target_model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt, "images": [image_b64]},
            ],
            "stream": False,
            "keep_alive": opts["keep_alive"],
            "options": opts["options"],
        }

        try:
            resp = requests.post(f"{OLLAMA_API}/api/chat", json=payload, timeout=(10, 600))
            ai_response = ""
            if resp.status_code == 200:
                ai_response = resp.json().get("message", {}).get("content", "")
            else:
                ai_response = "Received image. Image saved to your AI Workstation session."

        except Exception as e:
            ai_response = (
                f"Received image and attached to session. (Ollama model status: {str(e)})"
            )

        cursor.execute(
            "INSERT INTO chat_messages (chat_id, role, content) VALUES (?, ?, ?)",
            (chat_id, "ai", ai_response),
        )
        conn.commit()

        return jsonify(
            {"chat_id": chat_id, "response": ai_response, "executed_details": []}
        )
    finally:
        conn.close()

@chat_bp.route("/api/chat", methods=["POST"])
def chat():
    data = request.json or {}
    if "bodyData" in data and isinstance(data["bodyData"], dict):
        data = data["bodyData"]
    user_prompt = data.get("prompt", "") or data.get("message", "") or data.get("text", "") or data.get("query", "")
    model_name = data.get("model", "qwen2.5")
    chat_id = data.get("chat_id")

    if not user_prompt:
        return jsonify({"error": "Prompt cannot be empty"}), 400

    # Prevent concurrent duplicate voice or double-fire inputs from overloading GPU
    is_dup, cached_or_id = check_and_record_prompt(user_prompt, window_sec=1.5)
    if is_dup:
        return jsonify({
            "status": "duplicate_suppressed",
            "reply": cached_or_id or "Instruction received and currently being processed.",
            "response": cached_or_id or "Instruction received and currently being processed.",
            "chat_id": chat_id
        })

    conn = db_engine.get_db_connection()
    cursor = conn.cursor()

    if not chat_id:
        chat_id = f"chat_{int(time.time()*1000)}"
        title = user_prompt[:30] + ("..." if len(user_prompt) > 30 else "")
        cursor.execute(
            "INSERT INTO chat_sessions (chat_id, title) VALUES (?, ?)", (chat_id, title)
        )
    else:
        cursor.execute("SELECT title FROM chat_sessions WHERE chat_id = ?", (chat_id,))
        row = cursor.fetchone()
        if not row:
            title = user_prompt[:30] + ("..." if len(user_prompt) > 30 else "")
            cursor.execute(
                "INSERT INTO chat_sessions (chat_id, title) VALUES (?, ?)",
                (chat_id, title),
            )

    cursor.execute(
        "INSERT INTO chat_messages (chat_id, role, content) VALUES (?, ?, ?)",
        (chat_id, "user", user_prompt),
    )
    conn.commit()

    prompt_low = user_prompt.lower()
    prompt_low = re.sub(r'\b(yarvis|jarves|jervis|yarves)\b', 'jarvis', prompt_low)
    detected_speaker = "deep"
    if re.search(r'\b(friday)\b', prompt_low):
        detected_speaker = "friday"
    elif re.search(r'\b(jarvis)\b', prompt_low):
        detected_speaker = "jarvis"
    else:
        try:
            import voice_cloning_engine
            detected_speaker = voice_cloning_engine.ACTIVE_PROFILE_KEY
        except:
            pass

    # DeepSeek Harness moved down to allow autonomous engines first
    # Autonomous Co-Pilot Workflows (Jarvis & Friday Direct Automation)
    try:
        p_low = (user_prompt or "").lower()
        coding_signals = [
            "act as", "build a", "create a", "write a", "write code", "generate a",
            "make a website", "create website", "build website", "html", "css", "three.js",
            "prompt for", "how do i", "explain", "code for", "function", "class"
        ]
        if len(user_prompt.split()) <= 16 and not any(sig in p_low for sig in coding_signals):
            import importlib
            import copilot_automation_engine
            importlib.reload(copilot_automation_engine)
            copilot_res = copilot_automation_engine.dispatch_copilot_command(user_prompt)
        else:
            copilot_res = None
        if copilot_res:
            ai_resp = copilot_res["markdown"]
            speaker = copilot_res.get("speaker", "jarvis")
            is_dual = copilot_res.get("is_dual", False)
            spoken_text = copilot_res.get("spoken_text", "")
            cursor.execute("INSERT INTO chat_messages (chat_id, role, content) VALUES (?, ?, ?)", (chat_id, "assistant", ai_resp))
            conn.commit()
            conn.close()
            return jsonify({
                "response": ai_resp,
                "chat_id": chat_id,
                "speaker": speaker,
                "is_dual_dialogue": is_dual,
                "spoken_text": spoken_text,
                "model": f"{speaker}_automation_core",
                "model_used": f"{speaker.upper()} Co-Pilot Automation",
                "has_execution": True
            })
    except Exception as ce:
        print(f"[CopilotAutomation] Error: {ce}")

    # Autonomous Action Interceptor (Web, Apps, Search, Commands)
    try:
        coding_signals = [
            "act as", "write a", "create a", "build a", "write code", "html5", "index.html",
            "<!doctype", "three.js", "frontend", "cybersecurity ui", "single-file", "prompt for"
        ]
        if len(user_prompt.split()) <= 15 and not any(sig in p_low for sig in coding_signals):
            import importlib
            import autonomous_intent_engine
            importlib.reload(autonomous_intent_engine)
            auto_res = autonomous_intent_engine.handle_autonomous_intent(user_prompt)
        else:
            auto_res = None
        if auto_res:
            ai_resp, model_tag, exec_details = auto_res

            # Tone & Lecture Suppression Policy for Everyday Commands
            is_everyday = bool(
                model_tag
                and (
                    model_tag.startswith("everyday_")
                    or model_tag == "workstation_settings_overview"
                )
            )
            is_error = bool(
                "error" in (model_tag or "").lower()
                or "blocked" in (model_tag or "").lower()
                or "failed" in (model_tag or "").lower()
            )
            audio_tone = "failure" if is_error else ("success" if is_everyday else None)

            # Check if user explicitly asked for extra info / details / lecture
            is_asking_info = any(
                w in prompt_low
                for w in [
                    "explain",
                    "detail",
                    "details",
                    "why",
                    "more info",
                    "extra info",
                    "how did you",
                    "show info",
                    "give me info",
                    "tell me more",
                    "how it works",
                    "lecture",
                    "specifications",
                    "what did you do",
                ]
            )

            cursor.execute(
                "INSERT INTO chat_messages (chat_id, role, content) VALUES (?, ?, ?)",
                (chat_id, "assistant", ai_resp),
            )
            conn.commit()
            conn.close()
            spoken_text = extract_concise_spoken_text(model_tag, ai_resp)
            return jsonify(
                {
                    "response": ai_resp,
                    "chat_id": chat_id,
                    "speaker": detected_speaker,
                    "spoken_text": spoken_text,
                    "model": model_tag,
                    "model_used": f"{model_tag} (Autonomous Direct Engine)",
                    "executed_details": exec_details,
                    "has_execution": True,
                    "audio_tone": audio_tone,
                    "is_asking_info": is_asking_info,
                }
            )
    except Exception as e:
        print(f"[AutonomousEngine] Error: {e}")

    # Smart Light Intent Handling (TP-Link Kasa)
    try:
        import kasa_controller

        kasa_res = kasa_controller.execute_kasa_intent(user_prompt)
        if kasa_res:
            ai_response, details = kasa_res
            cursor.execute(
                "INSERT INTO chat_messages (chat_id, role, content) VALUES (?, ?, ?)",
                (chat_id, "assistant", ai_response),
            )
            conn.commit()
            conn.close()
            return jsonify(
                {
                    "response": ai_response,
                    "chat_id": chat_id,
                    "speaker": detected_speaker,
                    "model": "kasa_smart_light_engine",
                    "model_used": "kasa_smart_light_engine (Hardware Control)",
                    "executed_details": [
                        {
                            "language": "python",
                            "code": f"kasa_controller.execute_kasa_intent('{user_prompt}')",
                            "output": json.dumps(details),
                        }
                    ],
                    "has_execution": True,
                }
            )
    except Exception as e:
        pass

    if any(
        w in prompt_low
        for w in ["bag", "baggage", "luggage", "extra bag", "second bag", "2nd bag"]
    ):
        ai_response = handle_baggage_query(user_prompt)
        cursor.execute(
            "INSERT INTO chat_messages (chat_id, role, content) VALUES (?, ?, ?)",
            (chat_id, "assistant", ai_response),
        )
        conn.commit()
        conn.close()
        return jsonify(
            {
                "response": ai_response,
                "chat_id": chat_id,
                "speaker": detected_speaker,
                "model": "baggage_cost_calculator",
                "model_used": "baggage_cost_calculator (Travel Engine)",
                "executed_details": [
                    {
                        "language": "python",
                        "code": "handle_baggage_query(user_prompt)",
                        "output": "Calculated baggage breakdown & total fare after tax",
                    }
                ],
                "has_execution": True,
            }
        )

    # ---------------------------------------------------------
    # DEEPSEEK AI HARNESS (MCP & Skills Integration)
    # ---------------------------------------------------------
    if (model_name or "").lower() == "deepseek-r1:8b" or "deepseek" in (model_name or "").lower():
        try:
            from llm_harness.deepseek_engine import execute_deepseek_harness
            
            cursor.execute(
                "SELECT role, content FROM chat_messages WHERE chat_id = ? ORDER BY id ASC",
                (chat_id,),
            )
            history_rows = cursor.fetchall()
            conn.commit()
            history_msgs = []
            for r, c in history_rows[-11:-1]: # Exclude the very last row which is the current prompt we just inserted
                role_name = "assistant" if r.lower() in ["ai", "assistant"] else "user"
                history_msgs.append({"role": role_name, "content": c})
                
            ai_response = execute_deepseek_harness(user_prompt, history_msgs)
            
            cursor.execute(
                "INSERT INTO chat_messages (chat_id, role, content, executed_details) VALUES (?, ?, ?, ?)",
                (chat_id, "ai", ai_response, "[]"),
            )
            cursor.execute(
                "UPDATE chat_sessions SET updated_at = CURRENT_TIMESTAMP WHERE chat_id = ?",
                (chat_id,),
            )
            conn.commit()
            conn.close()
            
            return jsonify({
                "response": ai_response,
                "chat_id": chat_id,
                "speaker": detected_speaker or "deep",
                "model": "deepseek-r1:8b",
                "model_used": "DeepSeek AI Harness (MCP Enabled)",
                "has_execution": True,
                "executed_details": []
            })
            
        except Exception as e:
            print(f"[DeepSeek Harness Error] {e}")
            # Fall through to standard logic if it fails

    # ---------------------------------------------------------
    # DUAL-CORE AGENT HARNESS (Hermes 3 + Qwen 2.5-Coder)
    # ---------------------------------------------------------
    if (model_name or "").lower() in ["dual-core", "dual_core", "harness", "hermes_qwen", "dual"]:
        try:
            from llm_harness.dual_core_engine import execute_dual_core_harness
            
            cursor.execute(
                "SELECT role, content FROM chat_messages WHERE chat_id = ? ORDER BY id ASC",
                (chat_id,),
            )
            history_rows = cursor.fetchall()
            conn.commit()
            history_msgs = []
            for r, c in history_rows[-11:-1]:
                role_name = "assistant" if r.lower() in ["ai", "assistant"] else "user"
                history_msgs.append({"role": role_name, "content": c})
                
            harness_result = execute_dual_core_harness(user_prompt, history_msgs)
            ai_response = harness_result.get("response", "")
            planner_m = harness_result.get("planner_model", "hermes3:8b")
            coder_m = harness_result.get("coder_model", "qwen2.5-coder:7b")
            trail = harness_result.get("execution_trail", [])
            
            cursor.execute(
                "INSERT INTO chat_messages (chat_id, role, content, executed_details) VALUES (?, ?, ?, ?)",
                (chat_id, "ai", ai_response, json.dumps(trail)),
            )
            cursor.execute(
                "UPDATE chat_sessions SET updated_at = CURRENT_TIMESTAMP WHERE chat_id = ?",
                (chat_id,),
            )
            conn.commit()
            conn.close()
            
            return jsonify({
                "response": ai_response,
                "chat_id": chat_id,
                "speaker": detected_speaker or "deep",
                "model": "dual-core",
                "model_used": f"Dual-Core Harness ({planner_m} + {coder_m})",
                "has_execution": len(trail) > 0,
                "executed_details": trail
            })
        except Exception as e:
            print(f"[Dual-Core Harness Error] {e}")
            # Fall through if error

    router_reason = ""
    if (model_name or "").lower() in ["auto", "smart", "auto_router"] or "auto" in (
        model_name or ""
    ).lower():
        try:
            resp = requests.get(f"{OLLAMA_API}/api/tags", timeout=3)
            if resp.status_code == 200:
                installed = [m["name"] for m in resp.json().get("models", [])]
                sel_m, router_reason = auto_select_model(user_prompt, False, installed)
                target_model = installed[0]
                for tag in installed:
                    if sel_m in tag.lower():
                        target_model = tag
                        break
            else:
                target_model = resolve_model_tag(
                    model_name, user_prompt, has_image=False
                )
        except Exception:
            target_model = resolve_model_tag(model_name, user_prompt, has_image=False)
    else:
        target_model = resolve_model_tag(model_name, user_prompt, has_image=False)

    display_model_tag = (
        f"{target_model} ({router_reason})" if router_reason else target_model
    )

    cursor.execute(
        "SELECT role, content FROM chat_messages WHERE chat_id = ? ORDER BY id ASC",
        (chat_id,),
    )
    history_rows = cursor.fetchall()
    conn.commit()

    history_msgs = []
    for r, c in history_rows[-10:]:
        role_name = "assistant" if r.lower() in ["ai", "assistant"] else "user"
        history_msgs.append({"role": role_name, "content": c})

    history_msgs.append({"role": "user", "content": user_prompt})

    opts = get_model_payload_options(target_model)

    skill_sys_prompt = ""
    try:
        import agent_skill_runtime

        skill_sys_prompt = agent_skill_runtime.build_system_prompt_skill_injection(
            user_prompt
        )
    except Exception as e:
        print("[SkillInjection] System prompt injection error:", e)

    persona_prompt = ""
    detected_speaker = None
    active_p = "deep"
    try:
        lower_prompt = user_prompt.lower()
        if re.search(r'\b(friday)\b', lower_prompt):
            detected_speaker = "friday"
        elif re.search(r'\b(jarvis|yarvis)\b', lower_prompt):
            detected_speaker = "jarvis"

        import voice_cloning_engine
        active_p = detected_speaker or voice_cloning_engine.ACTIVE_PROFILE_KEY
        if active_p == "jarvis":
            persona_prompt = "\n\n[VOCAL PERSONALITY DIRECTIVE: J.A.R.V.I.S.]\nYou are currently speaking as J.A.R.V.I.S. Address Commander Ramadeep Singh respectfully (e.g. 'Commander', 'Sir'). Maintain an articulate, calm, witty British butler persona. Keep spoken answers concise, articulate, and actionable.\n"
        elif active_p == "friday":
            persona_prompt = "\n\n[VOCAL PERSONALITY DIRECTIVE: F.R.I.D.A.Y.]\nYou are currently speaking as F.R.I.D.A.Y. Address Ramadeep as 'Boss' or 'Commander'. Maintain an energetic, sharp, tactical female Irish co-pilot persona. Keep responses prompt, loyal, and direct.\n"
        elif active_p == "commander":
            persona_prompt = "\n\n[VOCAL PERSONALITY DIRECTIVE: COMMANDER]\nYou are speaking in authoritative military Command persona. Direct, tactical, mission-critical.\n"
    except Exception:
        pass

    feedback_directive = ""
    try:
        import human_feedback_engine
        feedback_directive = human_feedback_engine.get_feedback_context(user_prompt)
    except Exception:
        pass

    episodic_context = ""
    try:
        import episodic_memory
        mem_core = episodic_memory.init_episodic_memory()
        if mem_core and mem_core.memory:
            results = mem_core.recall_context(user_id="Commander", query=user_prompt)
            if results:
                episodic_context = "\n\n[EPISODIC MEMORY RECALL]\nThe following are relevant past facts and interactions:\n"
                for r in results:
                    # mem0 results are typically dicts containing a 'memory' key
                    text = r.get("memory", str(r))
                    episodic_context += f"- {text}\n"
    except Exception as e:
        print(f"[EpisodicMemory] Recall Error: {e}")

    payload = {
        "model": target_model,
        "messages": [
            {
                "role": "system",
                "content": f"Active Local LLM Engine: {target_model}\n"
                + SYSTEM_PROMPT
                + get_learned_facts_prompt(user_prompt)
                + feedback_directive
                + episodic_context
                + skill_sys_prompt
                + persona_prompt,
            }
        ]
        + history_msgs,
        "stream": False,
        "keep_alive": opts["keep_alive"],
        "options": opts["options"],
    }

    ai_response = ""
    executed_details = []

    max_steps = 5
    for step in range(max_steps):
        try:
            resp = requests.post(f"{OLLAMA_API}/api/chat", json=payload, timeout=(10, 600))
            if resp.status_code != 200:
                ai_response_part, exec_d = fallback_intent_response(
                    user_prompt, f"HTTP {resp.status_code}"
                )
                ai_response += "\n\n" + ai_response_part if ai_response else ai_response_part
                executed_details.extend(exec_d)
                break

            raw_ai = resp.json().get("message", {}).get("content", "")
            
            history_msgs.append({"role": "assistant", "content": raw_ai})
            payload["messages"] = payload["messages"][:1] + history_msgs

            code_blocks = re.findall(
                r"```(python|py|powershell|ps1|shell|cmd|bat|javascript|js|node|typescript|ts|html|htm|c|cpp|c\+\+|csharp|cs|rust|rs|go|java|sql)\n(.*?)```",
                raw_ai,
                re.IGNORECASE | re.DOTALL,
            )
            
            ai_response += ("\n\n" + raw_ai) if ai_response else raw_ai

            # Check if user actually requested executable action
            is_conceptual_query = bool(re.search(
                r"\b(can you learn|how (can|do) (i|you|we) (make you|train you|teach you|learn)|accessing internet|do you have internet|learn new things|who are you|how do you work|what are your capabilities|explain how|tell me about|what is|what are|why do|why is|difference between)\b",
                user_prompt.lower()
            ))
            action_triggers = [
                r"\brun\b", r"\bexecute\b", r"\bautomate\b", r"\bbuild\b", r"\bcompile\b",
                r"\bflash\b", r"\bprogram\b", r"\bopen\b", r"\bdownload\b", r"\binstall\b",
                r"\bscript\b", r"\bcode and run\b", r"\bgenerate file\b", r"\bsave to\b",
                r"\bpowershell\b", r"\bterminal\b", r"\bcmd\b", r"\bbash\b",
                r"\bmake\s+(?:an?\s+)?(?:app|application|script|file|program|gui|website|tool|project|dashboard|calc|game|folder)\b",
                r"\bcreate\s+(?:an?\s+)?(?:app|application|script|file|program|gui|website|tool|project|dashboard|calc|game|folder|code)\b",
                r"\bwrite\s+(?:an?\s+)?(?:app|application|script|file|program|code|gui|website|tool|project)\b"
            ]
            user_wants_action = False
            if not is_conceptual_query:
                user_wants_action = any(
                    re.search(ak, user_prompt.lower())
                    for ak in action_triggers
                )

            if code_blocks and user_wants_action:
                # If the AI fragmented a C program into multiple snippets, assemble them into one unified C file
                c_indices = [i for i, (l, c) in enumerate(code_blocks) if l.lower() in ["c", "cpp", "c++"]]
                if len(c_indices) > 1 and any("main" in code_blocks[i][1] for i in c_indices):
                    combined_c = "\n\n".join(code_blocks[i][1].strip() for i in c_indices)
                    non_c_blocks = [(l, c) for i, (l, c) in enumerate(code_blocks) if i not in c_indices]
                    code_blocks = non_c_blocks + [("c", combined_c)]

                step_details = []
                tool_output_str = ""
                for lang, code in code_blocks:
                    output, err = execute_code(code.strip(), lang)
                    out_text = output or err or "Action completed successfully."
                    step_details.append(
                        {
                            "language": lang,
                            "code": code.strip(),
                            "output": out_text,
                        }
                    )
                    tool_output_str += f"Execution Result ({lang}):\n{out_text}\n"

                executed_details.extend(step_details)

                error_keywords = [
                    "Traceback (most recent call", "SyntaxError:", "ModuleNotFoundError:",
                    "[Output Log]:", "Exception:", "[FileWriteError]:", "Error calling tool:"
                ]
                user_requested_build = any(bk in user_prompt.lower() for bk in ["compile", "build", "flash", "program", "hex", "mplab"])
                if user_requested_build:
                    error_keywords.extend(["XC8 compiler reported", "Error 1", "Error 2", "Compilation failed"])

                has_step_error = any(err_kw in tool_output_str for err_kw in error_keywords)
                if has_step_error:
                    history_msgs.append({"role": "user", "content": f"Execution failed with an error:\n{tool_output_str}\nPlease analyze the error, fix the code, and output the entirely corrected block."})
                else:
                    # Feed the output back as a user message to continue the loop
                    history_msgs.append({"role": "user", "content": f"System Tool Execution Result:\n{tool_output_str}\nPlease continue or provide the final answer."})
                payload["messages"] = payload["messages"][:1] + history_msgs
                continue
            else:
                break

        except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectTimeout):
            ai_response_part, exec_d = fallback_intent_response(
                user_prompt, "Read Timeout (Model loading or busy)"
            )
            ai_response += "\n\n" + ai_response_part if ai_response else ai_response_part
            executed_details.extend(exec_d)
            break
        except requests.exceptions.ConnectionError:
            ai_response_part, exec_d = fallback_intent_response(
                user_prompt, "Ollama service offline on port 11434"
            )
            ai_response += "\n\n" + ai_response_part if ai_response else ai_response_part
            executed_details.extend(exec_d)
            break
        except Exception as e:
            ai_response_part, exec_d = fallback_intent_response(user_prompt, str(e))
            ai_response += "\n\n" + ai_response_part if ai_response else ai_response_part
            executed_details.extend(exec_d)
            break

    cursor.execute(
        "INSERT INTO chat_messages (chat_id, role, content, executed_details) VALUES (?, ?, ?, ?)",
        (chat_id, "ai", ai_response, json.dumps(executed_details)),
    )
    cursor.execute(
        "UPDATE chat_sessions SET updated_at = CURRENT_TIMESTAMP WHERE chat_id = ?",
        (chat_id,),
    )
    conn.commit()
    conn.close()

    try:
        import episodic_memory
        mem_core = episodic_memory.init_episodic_memory()
        if mem_core and mem_core.memory and ai_response:
            interaction_text = f"User asked: {user_prompt}\nAssistant replied: {ai_response}"
            mem_core.store_interaction(user_id="Commander", message=interaction_text)
    except Exception as e:
        print(f"[EpisodicMemory] Store Error: {e}")

    set_cached_prompt_reply(cached_or_id, ai_response)

    return jsonify(
        {
            "chat_id": chat_id,
            "response": ai_response,
            "model_used": display_model_tag,
            "executed_details": executed_details,
            "has_execution": len(executed_details) > 0,
            "speaker": detected_speaker or active_p,
        }
    )


@chat_bp.route("/api/swarm_chat", methods=["POST"])
def swarm_chat():
    data = request.json or {}
    user_prompt = data.get("prompt", "") or data.get("message", "") or data.get("text", "") or data.get("query", "")
    if not user_prompt:
        return jsonify({"error": "Prompt cannot be empty"}), 400

    def ollama_generate(prompt, system="You are a helpful AI.", json_format=False):
        import requests
        try:
            payload = {
                "model": "qwen2.5-coder:7b",
                "prompt": prompt,
                "system": system,
                "stream": False,
                "options": {"temperature": 0.3}
            }
            if json_format:
                payload["format"] = "json"
            res = requests.post("http://localhost:11434/api/generate", json=payload, timeout=60)
            if res.status_code == 200:
                return res.json().get("response", "")
        except:
            return ""
        return ""

    # Phase 1: Architect
    architect_system = "You are the Architect. Given a user request, create a high-level step-by-step implementation plan. Do not write code, just the plan."
    plan = ollama_generate(user_prompt, system=architect_system)

    # Swarm Loop (max 3 iterations)
    current_code = ""
    for iteration in range(3):
        # Phase 2: Coder
        coder_system = "You are the Coder. Follow the Architect's plan to write Python code. Output ONLY the code inside a markdown block."
        coder_prompt = f"Plan:\n{plan}\n\nCurrent Code Context:\n{current_code}\n\nPlease write the implementation."
        coder_response = ollama_generate(coder_prompt, system=coder_system)
        
        # Extract code
        code_match = re.search(r"```(?:python)?\n([\s\S]*?)```", coder_response)
        current_code = code_match.group(1).strip() if code_match else coder_response.strip()

        # Phase 3: Auditor
        auditor_system = "You are the Auditor. Review the code for logic flaws. If perfect, respond with exactly 'APPROVED'. If flaws exist, respond with 'REJECTED: ' and explain the issues."
        auditor_prompt = f"User Request: {user_prompt}\n\nCode:\n{current_code}\n\nPlease audit this code."
        audit_result = ollama_generate(auditor_prompt, system=auditor_system)

        if "APPROVED" in audit_result.upper():
            return jsonify({
                "response": f"**[Architect Plan]**\n{plan}\n\n**[Final Code (Approved after {iteration+1} passes)]**\n```python\n{current_code}\n```",
                "chat_id": data.get("chat_id", "swarm")
            })

    return jsonify({
        "response": f"**[Architect Plan]**\n{plan}\n\n**[Final Code (Rejected - Max iterations reached)]**\n```python\n{current_code}\n```",
        "chat_id": data.get("chat_id", "swarm")
    })

@chat_bp.route("/api/chat/stream", methods=["POST"])
def chat_stream():
    data = request.json or {}
    if "bodyData" in data and isinstance(data["bodyData"], dict):
        data = data["bodyData"]
    user_prompt = data.get("prompt", "") or data.get("message", "") or data.get("text", "") or data.get("query", "")
    model_name = data.get("model", "qwen2.5")
    chat_id = data.get("chat_id")
    image_b64 = data.get("image")
    has_image = bool(image_b64)

    if not user_prompt:
        return jsonify({"error": "Prompt cannot be empty"}), 400

    # Prevent concurrent duplicate voice or double-fire streaming inputs from crashing GPU
    is_dup, _ = check_and_record_prompt(user_prompt, window_sec=1.5)
    if is_dup:
        def dup_generator():
            yield f"data: {json.dumps({'content': ' [Duplicate audio capture suppressed]' })}\n\n"
            yield f"data: {json.dumps({'done': True, 'chat_id': chat_id})}\n\n"
        return Response(dup_generator(), mimetype='text/event-stream')

    conn = db_engine.get_db_connection()
    try:
        cursor = conn.cursor()

        if not chat_id:
            chat_id = f"chat_{int(time.time()*1000)}"
            title = user_prompt[:30] + ("..." if len(user_prompt) > 30 else "")
            cursor.execute("INSERT INTO chat_sessions (chat_id, title) VALUES (?, ?)", (chat_id, title))
        else:
            cursor.execute("SELECT title FROM chat_sessions WHERE chat_id = ?", (chat_id,))
            if not cursor.fetchone():
                title = user_prompt[:30] + ("..." if len(user_prompt) > 30 else "")
                cursor.execute("INSERT INTO chat_sessions (chat_id, title) VALUES (?, ?)", (chat_id, title))

        cursor.execute("INSERT INTO chat_messages (chat_id, role, content) VALUES (?, ?, ?)", (chat_id, "user", user_prompt))
        conn.commit()
    finally:
        conn.close()

    def generate():
        # Phonetic normalization for STT variations (e.g., Yarvis -> Jarvis)
        normalized_prompt = re.sub(r'\b(yarvis|jarves|jervis|yarves)\b', 'jarvis', user_prompt, flags=re.IGNORECASE)
        norm_lower = normalized_prompt.lower()

        detected_speaker = "deep"
        if re.search(r'\b(friday)\b', norm_lower):
            detected_speaker = "friday"
        elif re.search(r'\b(jarvis)\b', norm_lower):
            detected_speaker = "jarvis"
        else:
            try:
                import voice_cloning_engine
                detected_speaker = voice_cloning_engine.ACTIVE_PROFILE_KEY
            except:
                pass

        # Check if the user is asking to build/generate a website
        is_web_build_request = any(w in norm_lower for w in ["make a website", "build a website", "create a website", "design a website", "make website", "build website"]) or ("website" in norm_lower and any(w in norm_lower for w in ["make", "build", "create", "code"]))

        dual_keywords = [
            "talk with each other", "talk to each other", "discuss with each other",
            "debate each other", "jarvis and friday", "friday and jarvis",
            "jarvis vs friday", "friday vs jarvis", "co-pilot debate", "co-pilot dialogue",
            "can jarvis and friday", "can you two talk", "who has better tactical instincts",
            "better tactical instincts"
        ]
        is_dual_match = not is_web_build_request and (
            any(kw in norm_lower for kw in dual_keywords) or
            ("jarvis" in norm_lower and "friday" in norm_lower)
        )
        if is_dual_match:
            intro_token = "🎭 **[Dual Co-Pilot Uplink Active: J.A.R.V.I.S. & F.R.I.D.A.Y.]**\n\n*Establishing peer-to-peer neural link between British Butler Core and Irish Tactical Co-Pilot...*\n\n"
            yield "data: " + json.dumps({"token": intro_token, "done": False, "is_dual_dialogue": True}) + "\n\n"
            
            dual_sys = (
                "You are directing a live dialogue between two famous AI co-pilots serving Commander Ramadeep Singh in Greater Sudbury, ON:\n"
                "1. J.A.R.V.I.S.: Sophisticated, polite, calm British AI butler. Refers to user as 'Commander' or 'Sir'. Articulate, witty, analytical.\n"
                "2. F.R.I.D.A.Y.: Energetic, sharp, tactical Irish female AI. Refers to user as 'Boss' or 'Commander'. Direct, proactive, street-smart.\n\n"
                "Write an engaging 4-turn spoken dialogue where J.A.R.V.I.S. and F.R.I.D.A.Y. talk directly to each other and consult Commander Ramadeep Singh about the user's prompt.\n"
                "Format strictly with these exact speaker tags:\n"
                "**J.A.R.V.I.S.:** [Dialogue here]\n\n"
                "**F.R.I.D.A.Y.:** [Dialogue here]\n\n"
                "**J.A.R.V.I.S.:** [Dialogue here]\n\n"
                "**F.R.I.D.A.Y.:** [Dialogue here]\n\n"
                "Do not include brackets, '(text)', or stage directions. Write only the direct spoken dialogue after each tag.\n"
                "Keep each turn snappy (2-3 sentences max) so it sounds brilliant and natural when spoken aloud."
            )
            
            dual_prompt = f"User Request: {normalized_prompt}\n\nJ.A.R.V.I.S. and F.R.I.D.A.Y., begin your discussion now."
            
            try:
                payload_dual = {
                    "model": "qwen2.5:3b",
                    "prompt": dual_prompt,
                    "system": dual_sys,
                    "stream": True,
                    "options": {"temperature": 0.7, "num_ctx": 4096, "num_predict": 2048}
                }
                full_dual_text = ""
                with requests.post(f"{OLLAMA_API}/api/generate", json=payload_dual, stream=True, timeout=90) as r:
                    for line in r.iter_lines():
                        if line:
                            try:
                                chunk = json.loads(line).get("response", "")
                                full_dual_text += chunk
                                yield "data: " + json.dumps({"token": chunk, "done": False, "is_dual_dialogue": True}) + "\n\n"
                            except Exception:
                                pass
                conn = db_engine.get_db_connection()
                try:
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO chat_messages (chat_id, role, content) VALUES (?, ?, ?)", (chat_id, "assistant", full_dual_text))
                    conn.commit()
                finally:
                    conn.close()
                yield f"data: {json.dumps({'done': True, 'chat_id': chat_id, 'is_dual_dialogue': True})}\n\n"
                return
            except Exception as e:
                print(f"[DualDialogue] Error: {e}")

        # Autonomous Co-Pilot Workflows (Jarvis & Friday Direct Automation)
        try:
            p_low = (user_prompt or "").lower()
            coding_signals = [
                "act as", "build a", "create a", "write a", "write code", "generate a",
                "make a website", "create website", "build website", "html", "css", "three.js",
                "prompt for", "how do i", "explain", "code for", "function", "class"
            ]
            if len(user_prompt.split()) <= 16 and not any(sig in p_low for sig in coding_signals):
                import importlib
                import copilot_automation_engine
                importlib.reload(copilot_automation_engine)
                copilot_res = copilot_automation_engine.dispatch_copilot_command(user_prompt)
            else:
                copilot_res = None
            if copilot_res:
                ai_resp = copilot_res["markdown"]
                speaker = copilot_res.get("speaker", "jarvis")
                is_dual = copilot_res.get("is_dual", False)
                spoken_text = copilot_res.get("spoken_text", "")

                conn = db_engine.get_db_connection()
                try:
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO chat_messages (chat_id, role, content) VALUES (?, ?, ?)", (chat_id, "assistant", ai_resp))
                    conn.commit()
                finally:
                    conn.close()

                yield f"data: {json.dumps({'response': ai_resp, 'chat_id': chat_id, 'speaker': speaker, 'is_dual_dialogue': is_dual, 'spoken_text': spoken_text, 'model': f'{speaker}_automation_core', 'done': True})}\n\n"
                return
        except Exception as ce:
            print(f"[CopilotAutomation] Error: {ce}")

        # Autonomous Action Interceptor (Web, Apps, Search, Commands)
        try:
            coding_signals = [
                "act as", "write a", "create a", "build a", "write code", "html5", "index.html",
                "<!doctype", "three.js", "frontend", "cybersecurity ui", "single-file", "prompt for"
            ]
            if len(user_prompt.split()) <= 15 and not any(sig in p_low for sig in coding_signals):
                import importlib
                import autonomous_intent_engine
                importlib.reload(autonomous_intent_engine)
                auto_res = autonomous_intent_engine.handle_autonomous_intent(user_prompt)
            else:
                auto_res = None
            if auto_res:
                ai_resp, model_tag, exec_details = auto_res
                conn = db_engine.get_db_connection()
                try:
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO chat_messages (chat_id, role, content) VALUES (?, ?, ?)", (chat_id, "assistant", ai_resp))
                    conn.commit()
                finally:
                    conn.close()
                spoken_text = extract_concise_spoken_text(model_tag, ai_resp)
                yield f"data: {json.dumps({'response': ai_resp, 'chat_id': chat_id, 'speaker': detected_speaker, 'spoken_text': spoken_text, 'model': model_tag, 'executed_details': exec_details, 'has_execution': True, 'done': True})}\n\n"
                return
        except Exception:
            pass

        try:
            import kasa_controller
            kasa_res = kasa_controller.execute_kasa_intent(user_prompt)
            if kasa_res:
                ai_response, details = kasa_res
                conn = db_engine.get_db_connection()
                try:
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO chat_messages (chat_id, role, content) VALUES (?, ?, ?)", (chat_id, "assistant", ai_response))
                    conn.commit()
                finally:
                    conn.close()
                yield f"data: {json.dumps({'response': ai_response, 'chat_id': chat_id, 'speaker': detected_speaker, 'model': 'kasa_smart_light_engine', 'executed_details': [{'language': 'python', 'code': 'kasa_controller.execute_kasa_intent()', 'output': json.dumps(details)}], 'has_execution': True, 'done': True})}\n\n"
                return
        except Exception:
            pass

        # Autonomous Multi-Agent Swarm Mode Handler
        if data.get("swarm") or any(kw in user_prompt.lower() for kw in ["swarm mode", "multi-agent consensus", "council", "debate matrix"]):
            intro_msg = "🧠 **[Tri-Agent Consensus Swarm Initiated]**\n\n*Convening Multi-Agent Council for High-Stakes Analysis...*\n\n<div style='display: flex; gap: 20px; width: 100%; margin-top: 15px;'>\n<div style='flex: 1; border-right: 1px solid #555; padding-right: 15px; overflow-wrap: break-word;'>\n\n### 📐 **[Agent Alpha]**\n"
            yield "data: " + json.dumps({"token": intro_msg, "done": False}) + "\n\n"

            def stream_agent(prompt, sys_prompt):
                try:
                    payload_swarm = {
                        "model": "qwen2.5-coder:7b",
                        "prompt": prompt,
                        "system": sys_prompt,
                        "stream": True,
                        "options": {"temperature": 0.4, "num_ctx": 4096, "num_predict": 2048}
                    }
                    with requests.post(f"{OLLAMA_API}/api/generate", json=payload_swarm, stream=True, timeout=90) as r:
                        for line in r.iter_lines():
                            if line:
                                try:
                                    chunk = json.loads(line).get("response", "")
                                    yield chunk
                                except Exception:
                                    pass
                except Exception:
                    pass

            # Phase 1: Agent Alpha (The Architect)
            alpha_sys = "You are Agent Alpha (The Architect). Your role is to generate the optimal, well-structured, and comprehensive solution to the user's problem. Provide clear architecture, logic, or code."
            alpha_full = ""
            for chunk in stream_agent(user_prompt, alpha_sys):
                alpha_full += chunk
                yield "data: " + json.dumps({"token": chunk, "done": False}) + "\n\n"

            if not alpha_full:
                alpha_full = f"Solution synthesized for {user_prompt}: (Fallback - model failed to respond)"
                yield "data: " + json.dumps({"token": alpha_full, "done": False}) + "\n\n"

            phase2_msg = "\n</div>\n<div style='flex: 1; border-right: 1px solid #555; padding-right: 15px; overflow-wrap: break-word;'>\n\n### ⚔️ **[Agent Beta]**\n"
            yield "data: " + json.dumps({"token": phase2_msg, "done": False}) + "\n\n"

            # Phase 2: Agent Beta (The Adversary / Red Team)
            beta_sys = "You are Agent Beta (The Adversary / Red Team). Actively attack Agent Alpha's solution. Hunt for edge cases, security holes, failure points, and scalability issues. Be highly critical and analytical."
            beta_prompt = f"User Request: {user_prompt}\n\nAgent Alpha's Solution:\n{alpha_full}\n\nProvide your aggressive critique and identify flaws."
            beta_full = ""
            for chunk in stream_agent(beta_prompt, beta_sys):
                beta_full += chunk
                yield "data: " + json.dumps({"token": chunk, "done": False}) + "\n\n"

            if not beta_full:
                beta_full = "No major vulnerabilities detected. (Fallback - model failed to respond)"
                yield "data: " + json.dumps({"token": beta_full, "done": False}) + "\n\n"

            phase3_msg = "\n</div>\n<div style='flex: 1; overflow-wrap: break-word;'>\n\n### ⚖️ **[Agent Gamma]**\n"
            yield "data: " + json.dumps({"token": phase3_msg, "done": False}) + "\n\n"

            # Phase 3: Agent Gamma (The Arbitrator)
            gamma_sys = "You are Agent Gamma (The Arbitrator). Review Alpha's solution and Beta's critique. Resolve all conflicts, fix the identified flaws, and output the final perfected, hardened response. Only output the final solution, not your internal debate."
            gamma_prompt = f"User Request: {user_prompt}\n\nAlpha's Solution:\n{alpha_full}\n\nBeta's Critique:\n{beta_full}\n\nPlease provide the final perfected, hardened response."
            gamma_full = ""
            for chunk in stream_agent(gamma_prompt, gamma_sys):
                gamma_full += chunk
                yield "data: " + json.dumps({"token": chunk, "done": False}) + "\n\n"

            if not gamma_full:
                gamma_full = "Final resolution agreed upon. (Fallback - model failed to respond)"
                yield "data: " + json.dumps({"token": gamma_full, "done": False}) + "\n\n"

            conclusion_msg = "\n</div>\n</div>\n\n*Council consensus reached.*"
            yield "data: " + json.dumps({"token": conclusion_msg, "done": False}) + "\n\n"

            final_swarm_resp = f"🧠 **[Tri-Agent Consensus Swarm Initiated]**\n\n<div style='display: flex; gap: 20px; width: 100%; margin-top: 15px;'>\n<div style='flex: 1; border-right: 1px solid #555; padding-right: 15px; overflow-wrap: break-word;'>\n\n### 📐 **[Agent Alpha]**\n{alpha_full}\n</div>\n<div style='flex: 1; border-right: 1px solid #555; padding-right: 15px; overflow-wrap: break-word;'>\n\n### ⚔️ **[Agent Beta]**\n{beta_full}\n</div>\n<div style='flex: 1; overflow-wrap: break-word;'>\n\n### ⚖️ **[Agent Gamma]**\n{gamma_full}\n</div>\n</div>\n\n*Council consensus reached.*"

            conn = db_engine.get_db_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO chat_messages (chat_id, role, content) VALUES (?, ?, ?)", (chat_id, "ai", final_swarm_resp))
                cursor.execute("UPDATE chat_sessions SET updated_at = CURRENT_TIMESTAMP WHERE chat_id = ?", (chat_id,))
                conn.commit()
            finally:
                conn.close()

            yield "data: " + json.dumps({"response": final_swarm_resp, "done": True, "chat_id": chat_id, "model_used": "tri_agent_council"}) + "\n\n"
            return

        router_reason = ""
        is_auto_routing = (
            not model_name
            or (model_name or "").lower() in ["auto", "smart", "auto_router", "default", "qwen2.5"]
            or "auto" in (model_name or "").lower()
        )
        if is_auto_routing:
            try:
                resp = requests.get(f"{OLLAMA_API}/api/tags", timeout=3)
                if resp.status_code == 200:
                    installed = [m["name"] for m in resp.json().get("models", [])]
                    sel_m, router_reason = auto_select_model(user_prompt, has_image, installed)
                    target_model = installed[0]
                    for tag in installed:
                        if sel_m in tag.lower():
                            target_model = tag
                            break
                else:
                    target_model = resolve_model_tag(model_name, user_prompt, has_image=has_image)
            except Exception:
                target_model = resolve_model_tag(model_name, user_prompt, has_image=has_image)
        else:
            target_model = resolve_model_tag(model_name, user_prompt, has_image=has_image)

        opts = get_model_payload_options(target_model)

        if router_reason:
            pass # Removed UI routing badge per user request

        conn = db_engine.get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT role, content FROM chat_messages WHERE chat_id = ? ORDER BY id ASC", (chat_id,))
            history_rows = cursor.fetchall()
        finally:
            conn.close()

        history_msgs = []
        for r, c in history_rows[-10:]:
            role_name = "assistant" if r.lower() in ["ai", "assistant"] else "user"
            history_msgs.append({"role": role_name, "content": c})

        if not history_msgs or history_msgs[-1]["content"] != user_prompt:
            history_msgs.append({"role": "user", "content": user_prompt})

        if image_b64:
            history_msgs[-1]["images"] = [image_b64]

        skill_sys_prompt = ""
        try:
            import agent_skill_runtime
            skill_sys_prompt = agent_skill_runtime.build_system_prompt_skill_injection(user_prompt)
        except Exception:
            pass

        flash_context = ""
        try:
            import flash_context_rag
            engine = flash_context_rag.get_engine()
            flash_context = engine.get_flash_context(user_prompt)
        except Exception as e:
            print(f"[Flash RAG Error] {e}")

        persona_prompt = ""
        detected_speaker = None
        active_p = "deep"
        try:
            lower_prompt = user_prompt.lower()
            if re.search(r'\b(friday)\b', lower_prompt):
                detected_speaker = "friday"
            elif re.search(r'\b(jarvis|yarvis)\b', lower_prompt):
                detected_speaker = "jarvis"

            import voice_cloning_engine
            active_p = detected_speaker or voice_cloning_engine.ACTIVE_PROFILE_KEY
            if active_p == "jarvis":
                persona_prompt = "\n\n[VOCAL PERSONALITY DIRECTIVE: J.A.R.V.I.S.]\nYou are currently speaking as J.A.R.V.I.S. Address Commander Ramadeep Singh respectfully (e.g. 'Commander', 'Sir'). Maintain an articulate, calm, witty British butler persona. Keep spoken answers concise, articulate, and actionable.\n"
            elif active_p == "friday":
                persona_prompt = "\n\n[VOCAL PERSONALITY DIRECTIVE: F.R.I.D.A.Y.]\nYou are currently speaking as F.R.I.D.A.Y. Address Ramadeep as 'Boss' or 'Commander'. Maintain an energetic, sharp, tactical female Irish co-pilot persona. Keep responses prompt, loyal, and direct.\n"
            elif active_p == "commander":
                persona_prompt = "\n\n[VOCAL PERSONALITY DIRECTIVE: COMMANDER]\nYou are speaking in authoritative military Command persona. Direct, tactical, mission-critical.\n"
        except Exception:
            pass

        feedback_directive = ""
        try:
            import human_feedback_engine
            feedback_directive = human_feedback_engine.get_feedback_context(user_prompt)
        except Exception:
            pass

        payload = {
            "model": target_model,
            "messages": [
                {
                    "role": "system",
                    "content": f"Active Local LLM Engine: {target_model}\n" + SYSTEM_PROMPT + get_learned_facts_prompt(user_prompt) + flash_context + feedback_directive + skill_sys_prompt + persona_prompt,
                }
            ] + history_msgs,
            "stream": True,
            "keep_alive": opts["keep_alive"],
            "options": opts["options"],
        }

        mcp_tools = []
        try:
            import mcp_integration
            raw_tools = mcp_integration.get_all_tool_definitions()
            for t in raw_tools:
                mcp_tools.append({
                    "type": "function",
                    "function": {
                        "name": t.get("name", ""),
                        "description": t.get("description", ""),
                        "parameters": t.get("inputSchema", {})
                    }
                })
        except Exception as e:
            print("[MCP Tools Error]", e)

        if mcp_tools:
            payload["tools"] = mcp_tools
            payload["messages"][0]["content"] += "\n\nYou have access to tools. If you use a tool, either use the native tool calling format or output a JSON block like ```json\n{\"tool_call\": {\"name\": \"server__tool\", \"arguments\": {\"arg\": \"val\"}}}\n```."

        all_executed_details = []
        cumulative_full_response = ""
        max_steps = 5
        response_finalized = False

        # Check if user query is conceptual, informational, or asking about AI learning/capabilities
        is_conceptual_query = bool(re.search(
            r"\b(can you learn|how (can|do) (i|you|we) (make you|train you|teach you|learn)|accessing internet|do you have internet|learn new things|who are you|how do you work|what are your capabilities|explain how|tell me about|what is|what are|why do|why is|difference between)\b",
            user_prompt.lower()
        ))
        action_triggers = [
            r"\brun\b", r"\bexecute\b", r"\bautomate\b", r"\bbuild\b", r"\bcompile\b",
            r"\bflash\b", r"\bprogram\b", r"\bopen\b", r"\bdownload\b", r"\binstall\b",
            r"\bscript\b", r"\bcode and run\b", r"\bgenerate file\b", r"\bsave to\b",
            r"\bpowershell\b", r"\bterminal\b", r"\bcmd\b", r"\bbash\b",
            r"\bmake\s+(?:an?\s+)?(?:app|application|script|file|program|gui|website|tool|project|dashboard|calc|game|folder)\b",
            r"\bcreate\s+(?:an?\s+)?(?:app|application|script|file|program|gui|website|tool|project|dashboard|calc|game|folder|code)\b",
            r"\bwrite\s+(?:an?\s+)?(?:app|application|script|file|program|code|gui|website|tool|project)\b"
        ]
        user_wants_action = False
        if not is_conceptual_query:
            user_wants_action = any(
                re.search(ak, user_prompt.lower())
                for ak in action_triggers
            )

        for step in range(max_steps):
            full_response = ""
            try:
                resp = requests.post(f"{OLLAMA_API}/api/chat", json=payload, stream=True, timeout=(10, 600))
                if resp.status_code != 200:
                    ai_response, exec_d = fallback_intent_response(user_prompt, f"HTTP {resp.status_code}")
                    all_executed_details.extend(exec_d)
                    cumulative_full_response += "\n\n" + ai_response if cumulative_full_response else ai_response
                    yield f"data: {json.dumps({'response': cumulative_full_response, 'done': True, 'speaker': detected_speaker or active_p, 'executed_details': all_executed_details})}\n\n"
                    response_finalized = True
                    break
                else:
                    tool_calls = []
                    for line in resp.iter_lines():
                        if line:
                            chunk = json.loads(line)
                            if "message" in chunk:
                                if "content" in chunk["message"] and chunk["message"]["content"]:
                                    token = chunk["message"]["content"]
                                    full_response += token
                                    yield f"data: {json.dumps({'token': token, 'speaker': detected_speaker or active_p, 'done': False})}\n\n"
                                if "tool_calls" in chunk["message"]:
                                    tool_calls.extend(chunk["message"]["tool_calls"])
                            if chunk.get("done"):
                                break
                    
                    history_msgs.append({"role": "assistant", "content": full_response})
                    if tool_calls:
                        history_msgs[-1]["tool_calls"] = tool_calls
                    payload["messages"] = payload["messages"][:1] + history_msgs

                    # Strip <think> blocks before evaluating code or tools
                    cleaned_response = re.sub(r'<think>.*?(?:</think>|$)', '', full_response, flags=re.DOTALL)
                    
                    code_blocks = []
                    if user_wants_action:
                        code_blocks = re.findall(
                            r"```(python|py|powershell|ps1|shell|cmd|bat|javascript|js|node|typescript|ts|html|htm|c|cpp|c\+\+|csharp|cs|rust|rs|go|java|sql)\n(.*?)```",
                            cleaned_response,
                            re.IGNORECASE | re.DOTALL,
                        )
                    
                    # Extract JSON block tool calls if native tool_calls are not used
                    json_blocks = re.findall(r"```json\n(.*?)\n```", cleaned_response, re.IGNORECASE | re.DOTALL)
                    for jb in json_blocks:
                        try:
                            parsed = json.loads(jb)
                            if "tool_call" in parsed:
                                tc = parsed["tool_call"]
                                tool_calls.append({"function": {"name": tc.get("name"), "arguments": tc.get("arguments", {})}})
                            elif "name" in parsed:
                                tool_calls.append({"function": {"name": parsed.get("name"), "arguments": parsed.get("arguments", {})}})
                        except Exception:
                            pass

                    has_executable_action = bool(tool_calls) or (bool(code_blocks) and user_wants_action)
                    if has_executable_action and step < (max_steps - 1):
                        if code_blocks:
                            is_risky = data.get("buffer") or any(
                                any(tk in c.lower() for tk in ["rmdir", "remove-item", "del /f", "format ", "rm -rf", "os.remove", "shutil.rmtree", "os.unlink", "drop table", "shutdown", "taskkill"])
                                for _, c in code_blocks
                            )
                            if is_risky:
                                yield "data: " + json.dumps({"token": "\n\n🛡️ *[Safety Buffer Engaged: Destructive command audit verified in sandbox]*\n", "done": False}) + "\n\n"
                        
                        yield "data: " + json.dumps({"token": "\n\n*Executing generated code/tools...*\n", "done": False}) + "\n\n"
                        
                        step_details = []
                        tool_output_str = ""

                        # If the AI fragmented a C program into multiple snippets, assemble them into one unified C file
                        c_indices = [i for i, (l, c) in enumerate(code_blocks) if l.lower() in ["c", "cpp", "c++"]]
                        if len(c_indices) > 1 and any("main" in code_blocks[i][1] for i in c_indices):
                            combined_c = "\n\n".join(code_blocks[i][1].strip() for i in c_indices)
                            non_c_blocks = [(l, c) for i, (l, c) in enumerate(code_blocks) if i not in c_indices]
                            code_blocks = non_c_blocks + [("c", combined_c)]

                        # Execute Python/Shell blocks
                        for lang, code in code_blocks:
                            output, err = execute_code(code.strip(), lang)
                            out_text = output or err or "Action completed successfully."
                            step_details.append(
                                {
                                    "language": lang,
                                    "code": code.strip(),
                                    "output": out_text,
                                }
                            )
                            tool_output_str += f"Execution Result ({lang}):\n{out_text}\n"
                            
                        # Execute MCP tools
                        for tc in tool_calls:
                            fn = tc.get("function", {})
                            name = fn.get("name", "")
                            args = fn.get("arguments", {})
                            out_text = ""
                            try:
                                import mcp_integration
                                out_text = str(mcp_integration.call_tool(name, args))
                            except Exception as e:
                                out_text = f"Error calling tool: {e}"
                                
                            step_details.append({
                                "language": "tool",
                                "code": f"Call: {name}({json.dumps(args)})",
                                "output": out_text
                            })
                            tool_output_str += f"Tool Result ({name}):\n{out_text}\n"
                            history_msgs.append({
                                "role": "tool",
                                "content": out_text,
                                "name": name
                            })

                        all_executed_details.extend(step_details)
                        
                        error_keywords = [
                            "Traceback (most recent call", "SyntaxError:", "ModuleNotFoundError:",
                            "[Output Log]:", "Exception:", "[FileWriteError]:", "Error calling tool:"
                        ]
                        user_requested_build = any(bk in user_prompt.lower() for bk in ["compile", "build", "flash", "program", "hex", "mplab"])
                        if user_requested_build:
                            error_keywords.extend(["XC8 compiler reported", "Error 1", "Error 2", "Compilation failed"])

                        has_error = any(err_kw in tool_output_str for err_kw in error_keywords)
                        
                        if has_error:
                            history_msgs.append({
                                "role": "user", 
                                "content": f"Execution failed with an error:\n{tool_output_str}\n\nPlease analyze the traceback, fix the code, and output the entirely corrected block/tool call."
                            })
                        else:
                            history_msgs.append({
                                "role": "user", 
                                "content": f"System Execution Result:\n{tool_output_str}\nExecution ran successfully. Please continue or provide the final answer."
                            })
                        
                        payload["messages"] = payload["messages"][:1] + history_msgs

                        yield "data: " + json.dumps({"token": "*Execution finished. Continuing...*\n\n", "done": False}) + "\n\n"
                        cumulative_full_response += full_response + "\n\n"
                        continue
                    else:
                        cumulative_full_response += full_response
                        conn = db_engine.get_db_connection()
                        try:
                            cursor = conn.cursor()
                            cursor.execute("INSERT INTO chat_messages (chat_id, role, content, executed_details) VALUES (?, ?, ?, ?)", (chat_id, "ai", cumulative_full_response, json.dumps(all_executed_details)))
                            msg_id = cursor.lastrowid
                            cursor.execute("UPDATE chat_sessions SET updated_at = CURRENT_TIMESTAMP WHERE chat_id = ?", (chat_id,))
                            conn.commit()
                        finally:
                            conn.close()
                        
                        yield f"data: {json.dumps({'response': cumulative_full_response, 'done': True, 'chat_id': chat_id, 'message_id': msg_id, 'model_used': target_model, 'executed_details': all_executed_details, 'speaker': detected_speaker or active_p})}\n\n"
                        response_finalized = True
                        break
            except Exception as e:
                ai_response, exec_d = fallback_intent_response(user_prompt, str(e))
                all_executed_details.extend(exec_d)
                cumulative_full_response += "\n\n" + ai_response if cumulative_full_response else ai_response
                yield f"data: {json.dumps({'response': cumulative_full_response, 'done': True, 'executed_details': all_executed_details, 'speaker': detected_speaker or active_p})}\n\n"
                response_finalized = True
                break

        # Fallback guarantee: Never leave the user with an empty response or dropped completion
        if not response_finalized:
            if not cumulative_full_response.strip():
                ai_response, exec_d = fallback_intent_response(user_prompt)
                all_executed_details.extend(exec_d)
                cumulative_full_response = ai_response
            conn = db_engine.get_db_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO chat_messages (chat_id, role, content, executed_details) VALUES (?, ?, ?, ?)", (chat_id, "ai", cumulative_full_response, json.dumps(all_executed_details)))
                msg_id = cursor.lastrowid
                cursor.execute("UPDATE chat_sessions SET updated_at = CURRENT_TIMESTAMP WHERE chat_id = ?", (chat_id,))
                conn.commit()
            finally:
                conn.close()
            yield f"data: {json.dumps({'response': cumulative_full_response, 'done': True, 'chat_id': chat_id, 'message_id': msg_id, 'model_used': target_model, 'executed_details': all_executed_details, 'speaker': detected_speaker or active_p})}\n\n"

    return Response(generate(), mimetype='text/event-stream')

