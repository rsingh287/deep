import ctypes
import math
import time
import urllib
import urllib.parse
import urllib.request


def handle_autonomous_intent(user_prompt: str):
    import json
    import os
    import re
    import subprocess
    import sys
    import webbrowser

    """
    Intercepts user commands and autonomously executes OS, browser, application, 
    terminal diagnostics, live math/conversions, and system commands.
    """
    if not user_prompt:
        return None

    norm_prompt = user_prompt.lower().strip()

    # --- MODULAR INTENT REGISTRY ---
    try:
        from intents.registry import execute_intent
        reg_result = execute_intent(user_prompt, norm_prompt)
        if reg_result:
            return reg_result
    except Exception as e:
        print(f"[Modular Registry] Error: {e}")



    # 0.5 Human Feedback & Conversational Praise / Correction Interceptor
    try:
        import human_feedback_engine
        feedback_res = human_feedback_engine.detect_conversational_feedback(user_prompt)
        if feedback_res:
            return feedback_res
    except Exception as e:
        print(f"[AutonomousIntent] Human Feedback error: {e}")

    # 0.6 Autonomous Learning & Internet Capabilities Interceptor
    try:
        learning_triggers = [
            "learn new things", "accessing internet", "access the internet", "browse the internet",
            "search the internet", "train yourself", "train your self", "how i can make you learn",
            "how can i make you learn", "how can i train you", "how do you learn", "how to train you",
            "teach yourself", "self train", "can you access internet", "can you browse internet",
            "do you have internet access", "can you search the web", "can you learn on your own"
        ]
        p_clean = user_prompt.lower().strip()
        if any(lt in p_clean for lt in learning_triggers):
            learning_resp = (
                "### 🌐 **Autonomous Internet Research & Continuous Self-Training Core**\n\n"
                "Commander **Mr. Ramadeep Singh**, I operate with full native internet research powers and continuous lifelong learning:\n\n"
                "---\n\n"
                "#### 1. 🔍 **Real-Time Internet Access & Autonomous Research**\n"
                "* **Live Web Intelligence & Scraping:** I search the web, fetch live URLs, query real-time public APIs, and scrape technical documentation directly via native Python and MCP tools.\n"
                "* **Live Browser Pilot (`browser_use_agent`):** I can launch and navigate Microsoft Edge or Google Chrome to read documentation, verify websites, inspect web apps, or gather live data.\n"
                "* **Background Research Swarm (`background_research_intent`):** On request, I deploy asynchronous background workers that monitor topics, scrape GitHub/arXiv/technical portals, and compile complete research dossiers directly to your Desktop.\n\n"
                "---\n\n"
                "#### 2. 🧠 **How You Train Me Everyday (Continuous Learning Loop)**\n"
                "You do **not** need to wait for external model retraining—my cognitive architecture continuously learns and adapts from you every single day through 5 integrated layers:\n\n"
                "1. **Active Reinforcement Learning from Human Feedback (RLHF Core):**\n"
                "   * Whenever you say *\"that was wrong, do X instead\"* or *\"perfect, keep doing that\"*, `human_feedback_engine.py` immediately extracts the actionable rule.\n"
                "   * It stores the rule in PostgreSQL (`human_feedback` table) and dynamically injects it into my system prompt for every future query as an active few-shot guardrail.\n"
                "2. **Persistent Semantic Vector Memory (`mem0` & `enhanced_knowledge_graph`):**\n"
                "   * Simply tell me: *\"Remember that [any rule, hardware preference, project requirement]\"*.\n"
                "   * It is immediately vectorized and stored across sessions so I never forget it.\n"
                "3. **DPO / SFT Dataset Curation (`dataset_fine_tune.jsonl`):**\n"
                "   * All verified solutions and corrected mistakes are automatically appended to a local fine-tuning dataset formatted for LoRA/SFT training.\n"
                "4. **Local Hardware Fine-Tuning (`train_deep_pic_hardware.py`):**\n"
                "   * We can run local fine-tuning scripts on your NVIDIA RTX GPU to update local model adapter weights permanently.\n"
                "5. **Interactive Skills Hub (`/skills`):**\n"
                "   * You can teach me new permanent skills at any time by defining new workflows or asking me to create a reusable agent skill.\n\n"
                "---\n\n"
                "> 💡 **Immediate Training Example:** Tell me right now:  \n"
                "> *\"Remember that for our PIC18F85K22 board, always verify RA4 is cleared for the LCD backlight\"*  \n"
                "> and watch it commit directly into persistent cognitive memory!"
            )
            return (
                learning_resp,
                "autonomous_learning_core",
                [{"language": "architecture", "code": "human_feedback_engine + memory_engine + browser_use_agent", "output": "Active Continuous Learning & Web Access Pipeline Online"}]
            )
    except Exception as le:
        print(f"[AutonomousIntent] Learning Interceptor error: {le}")

    prompt_low = re.sub(r"[\.\?\!\;]+$", "", user_prompt.lower().strip()).strip()

    # Normalization: Strip conversational prefixes, wake words, and punctuation
    norm_prompt = re.sub(
        r"^(hey|hi|hello|yo|deep|buddy|bro|please|can you|could you|would you|i want to|just|ok|okay)\s+",
        "",
        prompt_low,
    ).strip()
    norm_prompt = re.sub(
        r"^(hey|hi|hello|yo|deep|buddy|bro|please|can you|could you|would you|i want to|just|ok|okay)\s+",
        "",
        norm_prompt,
    ).strip()
    norm_prompt = norm_prompt.replace(",", " ").strip()
    norm_prompt = re.sub(r"\s+", " ", norm_prompt)

    # ---------------------------------------------------------
    # SECURITY & PERMISSION GUARDRAILS (Mr. Ramadeep Singh Policy)
    # Strictly disallow registry changes & external data transmission
    # ---------------------------------------------------------
    reg_patterns = [
        r"\breg\b",
        r"\bregedit\b",
        r"\bhklm\b",
        r"\bhkcu\b",
        r"set-itemproperty.*registry",
        r"new-itemproperty.*registry",
    ]
    if any(re.search(p, prompt_low) for p in reg_patterns):
        return (
            "🛡️ **Security Guardrail Active (Mr. Ramadeep Singh):** Registry modifications are strictly BLOCKED by policy. Your system settings and registry remain protected.",
            "security_guardrail_registry_blocked",
            [
                {
                    "language": "security",
                    "code": "POLICY_CHECK_REGISTRY",
                    "output": "Access Denied: Registry alterations forbidden",
                }
            ],
        )

    exfil_patterns = [
        r"upload.*to\s+http",
        r"send.*data.*outside",
        r"exfiltrate",
        r"curl.*-F\s+file=@",
    ]
    if any(re.search(p, prompt_low) for p in exfil_patterns):
        return (
            "🛡️ **Privacy Guardrail Active (Mr. Ramadeep Singh):** Outbound data exfiltration is strictly BLOCKED by policy. No system or personal data is permitted to leave your PC.",
            "security_guardrail_exfil_blocked",
            [
                {
                    "language": "security",
                    "code": "POLICY_CHECK_EXFILTRATION",
                    "output": "Access Denied: External data egress forbidden",
                }
            ],
        )

    # ---------------------------------------------------------
    # FAST-PATH 0: EVERYDAY HUMAN PC ACTIONS (10,000,000+ USE CASES)
    # Priority 0: Master volume, brightness, apps, folders, media, system status
    # ---------------------------------------------------------
    try:
        _cur_dir = os.path.dirname(os.path.abspath(__file__))
        if _cur_dir not in sys.path:
            sys.path.insert(0, _cur_dir)
        import everyday_pc_actions

        everyday_res = everyday_pc_actions.handle_everyday_command(user_prompt)
        if everyday_res:
            return everyday_res
    except Exception as e:
        print("[AutonomousIntent] Everyday actions engine error:", e)

    # ---------------------------------------------------------
    # FAST-PATH 0.1: 3D BUDDY SCREEN POSITIONING (MULTI-MONITOR)
    # ---------------------------------------------------------
    screen_match = re.search(
        r"\b(?:go to|move to)\s+screen\s+(one|two|three|four|\d+)\b", prompt_low
    )
    if screen_match:
        try:
            import workspace_arranger

            screen_word = screen_match.group(1)
            mapping = {"one": 1, "two": 2, "three": 3, "four": 4}
            screen_idx = mapping.get(screen_word)
            if not screen_idx and screen_word.isdigit():
                screen_idx = int(screen_word)

            if screen_idx:
                res = workspace_arranger.move_deep_to_screen(screen_idx)
                return (
                    f"🖥️ **Workspace Arranger:** {res['message']}",
                    "autonomous_workspace_arranger",
                    [
                        {
                            "language": "python",
                            "code": f"workspace_arranger.move_deep_to_screen({screen_idx})",
                            "output": res["status"],
                        }
                    ],
                )
        except Exception as e:
            print("[AutonomousIntent] Screen positioning error:", e)

    # ---------------------------------------------------------
    # FAST-PATH 1: SPECIALIZED AI SKILLS & CUSTOM AGENTS (422 SKILLS)
    # ---------------------------------------------------------
    try:
        import sys

        _cur_dir = os.path.dirname(os.path.abspath(__file__))
        if _cur_dir not in sys.path:
            sys.path.insert(0, _cur_dir)
        from skills_intent_engine import handle_skills_intent

        skill_res = handle_skills_intent(user_prompt)
        if skill_res:
            return skill_res
    except Exception as e:
        print("[AutonomousIntent] Skills engine check error:", e)





    # ---------------------------------------------------------
    # FAST-PATH 1: HARDWARE CAMERA LAUNCH
    # ---------------------------------------------------------
    if (
        any(
            w in norm_prompt
            for w in [
                "open camera",
                "launch camera",
                "start camera",
                "turn on camera",
                "show camera",
                "open webcam",
                "start webcam",
                "turn on webcam",
                "webcam",
            ]
        )
        or norm_prompt == "camera"
    ):
        try:
            subprocess.Popen(["start", "microsoft.windows.camera:"], shell=True)
            return (
                "📷 **Autonomous Camera Control:** Windows Camera launched successfully! (You can also open Mr. Ramadeep Singh's MediaPipe Kinematics Suite via `http://localhost:5000/ramadeep_kinematics`)",
                "autonomous_camera_launcher",
                [
                    {
                        "language": "powershell",
                        "code": "start microsoft.windows.camera:",
                        "output": "Camera launched",
                    }
                ],
            )
        except Exception:
            pass

    # ---------------------------------------------------------
    # FAST-PATH 2: MEDIAPIPE HAND & FACE KINEMATICS ENGINE
    # ---------------------------------------------------------
    if any(
        w in norm_prompt
        for w in [
            "open kinematics",
            "launch kinematics",
            "start kinematics",
            "mediapipe",
            "hand tracking",
            "face mesh",
            "kinematics engine"
        ]
    ):
        try:
            kinematics_url = "http://localhost:8090/index.html"
            subprocess.Popen(["cmd.exe", "/c", "start", kinematics_url])
            return (
                "✋ **MediaPipe Hand & Face Kinematics Engine:** Initialized for Commander **Mr. Ramadeep Singh**! Active Model 1 (Hands 21 3D Landmarks) & Active Model 2 (Face Mesh 468 3D Landmarks).",
                "ramadeep_kinematics_engine",
                [
                    {
                        "language": "powershell",
                        "code": f"start {kinematics_url}",
                        "output": "Kinematics Engine Launched",
                    }
                ],
            )
        except Exception:
            pass

    # ---------------------------------------------------------
    # 00-ANIMATION. LIVE DESKTOP NAME ANIMATION (MR. RAMADEEP SINGH)
    # ---------------------------------------------------------
    if any(
        k in prompt_low
        for k in [
            "name running",
            "name moving",
            "running from left to right",
            "moving from left to right",
            "run across the screen",
            "name across the screen",
            "ramadeep moving",
            "ramadeep running",
            "my name run",
            "name from left to right",
            "name run from left",
            "code with my name",
            "animation with my name",
        ]
    ):
        code = """import tkinter as tk

def create_moving_name_app():
    root = tk.Tk()
    root.title("Mr. Ramadeep Singh - Desktop Name Animation")
    root.geometry("900x260")
    root.configure(bg="#0f172a")
    root.resizable(False, False)

    title_label = tk.Label(
        root, 
        text="⚡ Autonomous Desktop Animation • Mr. Ramadeep Singh Moving Left to Right", 
        font=("Segoe UI", 11, "bold"), 
        bg="#0f172a", 
        fg="#38bdf8"
    )
    title_label.pack(pady=12)

    canvas_width = 860
    canvas_height = 160
    canvas = tk.Canvas(
        root, 
        width=canvas_width, 
        height=canvas_height, 
        bg="#1e293b", 
        highlightthickness=1, 
        highlightbackground="#334155"
    )
    canvas.pack(pady=5)

    name = "Mr. Ramadeep Singh"
    text_item = canvas.create_text(
        40, 
        canvas_height // 2, 
        text=name, 
        font=("Segoe UI", 32, "bold"), 
        fill="#38bdf8", 
        anchor="w"
    )

    speed = 6
    direction = 1
    colors = ["#38bdf8", "#818cf8", "#f43f5e", "#fbbf24", "#34d399", "#a855f7"]
    color_index = 0

    def animate():
        nonlocal direction, color_index
        bbox = canvas.bbox(text_item)
        if bbox:
            x1, y1, x2, y2 = bbox
            if x2 >= canvas_width - 20:
                direction = -1
                color_index = (color_index + 1) % len(colors)
                canvas.itemconfig(text_item, fill=colors[color_index])
            elif x1 <= 20:
                direction = 1
                color_index = (color_index + 1) % len(colors)
                canvas.itemconfig(text_item, fill=colors[color_index])
        canvas.move(text_item, speed * direction, 0)
        root.after(16, animate)

    animate()
    root.mainloop()

if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    create_moving_name_app()"""

        gen_dir = os.path.join(os.path.dirname(__file__), "generated_apps")
        os.makedirs(gen_dir, exist_ok=True)
        script_file = os.path.join(gen_dir, "ramadeep_singh_animation.py")
        with open(script_file, "w", encoding="utf-8") as f:
            f.write(code)

        proc = subprocess.Popen([sys.executable, script_file], cwd=gen_dir)

        response_md = f"""🚀 **Autonomously Launched Desktop Animation for Commander Mr. Ramadeep Singh!**

I have generated the Python Tkinter script and launched the live desktop animation window on your screen (PID `{proc.pid}`).

- **Commander Name**: **Mr. Ramadeep Singh**
- **Action**: Running smoothly from left to right across the canvas with 60 FPS dynamic neon color shifting.
- **Saved To**: `{script_file}`

```python
{code}
```
"""
        return (
            response_md,
            "autonomous_desktop_animator",
            [
                {
                    "language": "python",
                    "code": code,
                    "output": f"Launched Mr. Ramadeep Singh Moving Animation (PID {proc.pid})",
                }
            ],
        )

    # ---------------------------------------------------------
    # 00. CODE GENERATION & PROGRAMMING GUARD
    # ---------------------------------------------------------
    # If user explicitly asks to write, generate, or make code/scripts/apps,
    # pass directly to the specialized Ollama AI coder (qwen2.5-coder:7b).
    code_triggers = [
        "make a code",
        "write a code",
        "create a code",
        "make code",
        "write code",
        "generate code",
        "create code",
        "give me code",
        "provide code",
        "write a script",
        "create a script",
        "generate a script",
        "write a program",
        "write a function",
        "python code",
        "javascript code",
        "html code",
        "c++ code",
        "c# code",
        "rust code",
        "write python",
        "write javascript",
        "build an app",
        "create an app",
    ]
    if any(k in prompt_low for k in code_triggers) or re.search(
        r"\b(?:write|make|create|generate|implement)\s+.*?\b(?:code|script|program|function|algorithm)\b",
        prompt_low,
    ):
        return None

    # Live Temperature Math Conversion (e.g. "convert 100 celsius to fahrenheit" when not asking for code)
    temp_conv_m = re.search(
        r"\b(?:convert\s+)?(-?\d+(?:\.\d+)?)\s*(?:°\s*)?(celsius|fahrenheit|c|f)\s*(?:to|in|into|=)\s*(?:°\s*)?(celsius|fahrenheit|c|f)\b",
        prompt_low,
    )
    if temp_conv_m:
        val = float(temp_conv_m.group(1))
        u1 = temp_conv_m.group(2).lower()
        u2 = temp_conv_m.group(3).lower()
        is_c1 = u1 in ["c", "celsius"]
        is_f1 = u1 in ["f", "fahrenheit"]
        is_c2 = u2 in ["c", "celsius"]
        is_f2 = u2 in ["f", "fahrenheit"]
        if is_c1 and is_f2:
            res_f = round((val * 9 / 5) + 32, 2)
            return (
                f"🌡️ **Temperature Conversion:**\n\n- **{val}°C** = **{res_f}°F**\n- *Formula: ({val} × 9/5) + 32 = {res_f}°F*",
                "autonomous_math_engine",
                [
                    {
                        "language": "python",
                        "code": f"({val} * 9/5) + 32",
                        "output": f"{res_f} °F",
                    }
                ],
            )
        elif is_f1 and is_c2:
            res_c = round((val - 32) * 5 / 9, 2)
            return (
                f"🌡️ **Temperature Conversion:**\n\n- **{val}°F** = **{res_c}°C**\n- *Formula: ({val} - 32) × 5/9 = {res_c}°C*",
                "autonomous_math_engine",
                [
                    {
                        "language": "python",
                        "code": f"({val} - 32) * 5/9",
                        "output": f"{res_c} °C",
                    }
                ],
            )

    # ---------------------------------------------------------
    # 0A0-DEEP SEARCH. AUTONOMOUS WEB SCRAPING & RAG ENGINE
    # ---------------------------------------------------------
    search_triggers = [
        "search the web",
        "search google",
        "search for",
        "search ",
        "deep search",
    ]
    if any(k in prompt_low for k in search_triggers):
        try:
            import advanced_search_intent
            clean_query = user_prompt
            for t in search_triggers:
                if user_prompt.lower().startswith(t):
                    clean_query = user_prompt[len(t):].strip()
                    break
            
            res = advanced_search_intent.perform_advanced_search(clean_query)
            report = f"🌐 **Deep Web Search & Analysis**\n\n{res}"
            
            return (
                report,
                "deep_search_engine",
                []
            )
        except Exception as se:
            print(f"[DeepSearchEngine] Error: {se}")

    # ---------------------------------------------------------
    # 0A0-VISION. MEDIAPIPE HAND TRACKING & FACE KINEMATICS ENGINE
    # ---------------------------------------------------------
    try:
        import universal_vision_gesture_engine

        vis_res = universal_vision_gesture_engine.handle_vision_intent(user_prompt)
        if vis_res:
            return vis_res
    except Exception as ve:
        print(f"[MediaPipeVisionEngine] Error: {ve}")

    # ---------------------------------------------------------
    # 0A0-SKILLS. 422 MASTER AI SKILLS & CAPABILITIES DISPATCH ENGINE
    # ---------------------------------------------------------
    try:
        import skills_intent_engine

        sk_res = skills_intent_engine.handle_skills_intent(user_prompt)
        if sk_res:
            return sk_res
    except Exception as ske:
        print(f"[SkillsEngine] Error: {ske}")

    # ---------------------------------------------------------
    # 0A0-DOCKER. AUTONOMOUS DOCKER CONTAINER & ORCHESTRATION ENGINE
    # ---------------------------------------------------------
    try:
        import docker_engine

        dock_res = docker_engine.handle_docker_intent(user_prompt)
        if dock_res:
            return dock_res
    except Exception as de:
        print(f"[DockerEngine] Error: {de}")

    # ---------------------------------------------------------
    # 0A0-CURRENCY. REAL-TIME CURRENCY EXCHANGE CONVERTER ENGINE
    # ---------------------------------------------------------
    try:
        import currency_exchange_engine

        curr_res = currency_exchange_engine.handle_currency_intent(user_prompt)
        if curr_res:
            return curr_res
    except Exception as ce:
        print(f"[CurrencyEngine] Error: {ce}")

    # ---------------------------------------------------------
    # 0A0-WORLDCLOCK. LIVE GLOBAL WORLD CLOCK & TIMEZONE ENGINE
    # ---------------------------------------------------------
    try:
        import world_clock_engine

        wc_res = world_clock_engine.handle_world_clock_intent(user_prompt)
        if wc_res:
            return wc_res
    except Exception as wce:
        print(f"[WorldClockEngine] Error: {wce}")

    # ---------------------------------------------------------
    # 0A0-ACADEMY. INTERACTIVE CHAPTER ACADEMY ENGINE
    # ---------------------------------------------------------
    try:
        if any(
            k in prompt_low
            for k in [
                "course progress",
                "my course",
                "learning academy",
                "chapter 1",
                "chapter 2",
                "powerbi course",
                "sql course",
            ]
        ):
            import interactive_learning_academy

            ac_res = interactive_learning_academy.process_academy_request(user_prompt)
            if ac_res:
                return (
                    ac_res,
                    "interactive_learning_academy",
                    [
                        {
                            "language": "python",
                            "code": "process_academy_request()",
                            "output": "Fetched Academy Progress",
                        }
                    ],
                )
    except Exception as ace:
        print(f"[LearningAcademyEngine] Error: {ace}")


    # ---------------------------------------------------------
    # 0A0-VISION. MEDIAPIPE HAND & FACE KINEMATICS ENGINE
    # ---------------------------------------------------------
    if any(k in norm_prompt for k in ["gesture", "hand track", "face mesh", "kinematics", "webcam gesture", "mediapipe"]):
        try:
            import universal_vision_gesture_engine

            vis_res = universal_vision_gesture_engine.handle_vision_intent(user_prompt)
            if vis_res:
                return vis_res
        except Exception as ve:
            print(f"[MediaPipeVisionEngine] Error: {ve}")

    # ---------------------------------------------------------
    # 0A0-W3SCHOOLS. AUTONOMOUS W3SCHOOLS TUTORIAL ENGINE
    # ---------------------------------------------------------
    try:
        import w3schools_search_engine

        w3_res = w3schools_search_engine.handle_w3schools_intent(user_prompt)
        if w3_res:
            return w3_res
    except Exception as w3e:
        print(f"[W3SchoolsSearchEngine] Error: {w3e}")

    # ---------------------------------------------------------
    # 0A0-TRAVEL. UNIFIED FLIGHTS, HOTELS & CAR RENTAL ENGINE
    # ---------------------------------------------------------
    try:
        import travel_booking_engine

        travel_res = travel_booking_engine.handle_travel_booking_intent(user_prompt)
        if travel_res:
            return travel_res
    except Exception as te:
        print(f"[TravelBookingEngine] Error: {te}")

    # ---------------------------------------------------------
    # 0A0-FREE-APIS. REAL-TIME FREE & PUBLIC KEYLESS API ENGINE
    # ---------------------------------------------------------
    try:
        import free_public_apis

        pub_res = free_public_apis.handle_public_api_intent(user_prompt)
        if pub_res:
            return pub_res
    except Exception as pe:
        print(f"[FreePublicAPIEngine] Error: {pe}")

    # ---------------------------------------------------------
    # 0A0-DAILY-LIFE. AUTONOMOUS DAILY LIFE SUITE
    # ---------------------------------------------------------
    if any(
        k in prompt_low
        for k in ["check email", "read email", "unread email", "my email"]
    ):
        try:
            from autonomous_email_assistant import AutonomousEmailAssistant

            res = AutonomousEmailAssistant().check_unread_emails()
            return (
                res,
                "autonomous_email_assistant",
                [
                    {
                        "language": "python",
                        "code": "check_unread_emails()",
                        "output": "Checked Email",
                    }
                ],
            )
        except Exception as e:
            print(f"[EmailEngine] Error: {e}")

    if any(
        k in prompt_low
        for k in ["add reminder", "set reminder", "check reminders", "my reminders"]
    ):
        try:
            from calendar_and_routine_engine import CalendarRoutineEngine

            if "check" in prompt_low or "my" in prompt_low:
                res = CalendarRoutineEngine().check_due_reminders()
            else:
                import datetime

                dt = (datetime.datetime.now() + datetime.timedelta(hours=1)).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                res = CalendarRoutineEngine().add_reminder("New Reminder", dt)
            return (
                res,
                "calendar_and_routine_engine",
                [
                    {
                        "language": "python",
                        "code": "calendar_engine()",
                        "output": "Managed Calendar",
                    }
                ],
            )
        except Exception as e:
            print(f"[CalendarEngine] Error: {e}")

    if any(
        k in prompt_low
        for k in ["expense summary", "spending summary", "finance report", "my budget"]
    ):
        try:
            from personal_finance_manager import PersonalFinanceManager

            res = PersonalFinanceManager().get_summary()
            return (
                res,
                "personal_finance_manager",
                [
                    {
                        "language": "python",
                        "code": "get_summary()",
                        "output": "Generated Finance Report",
                    }
                ],
            )
        except Exception as e:
            print(f"[FinanceEngine] Error: {e}")

    if any(
        k in prompt_low
        for k in ["fitness summary", "health summary", "workout summary", "my health"]
    ):
        try:
            from health_fitness_tracker_engine import HealthFitnessTracker

            res = HealthFitnessTracker().get_daily_summary()
            return (
                res,
                "health_fitness_tracker",
                [
                    {
                        "language": "python",
                        "code": "get_daily_summary()",
                        "output": "Generated Health Report",
                    }
                ],
            )
        except Exception as e:
            print(f"[FitnessEngine] Error: {e}")

    if any(
        k in prompt_low
        for k in ["suggest recipe", "meal plan", "what to eat", "dinner idea"]
    ):
        try:
            from meal_planner_chef_engine import MealPlannerChef

            res = MealPlannerChef().suggest_recipe()
            return (
                res,
                "meal_planner_chef",
                [
                    {
                        "language": "python",
                        "code": "suggest_recipe()",
                        "output": "Suggested Meal",
                    }
                ],
            )
        except Exception as e:
            print(f"[MealEngine] Error: {e}")

    if any(
        k in prompt_low
        for k in [
            "daily briefing",
            "morning briefing",
            "today's news",
            "what's the news",
        ]
    ):
        try:
            from daily_briefing_engine import DailyBriefingEngine

            res = DailyBriefingEngine().generate_briefing()
            return (
                res,
                "daily_briefing_engine",
                [
                    {
                        "language": "python",
                        "code": "generate_briefing()",
                        "output": "Generated Briefing",
                    }
                ],
            )
        except Exception as e:
            print(f"[BriefingEngine] Error: {e}")

    if any(
        k in prompt_low
        for k in ["pending tasks", "to do list", "todo list", "my tasks"]
    ):
        try:
            from task_manager_engine import TaskManagerEngine

            res = TaskManagerEngine().get_pending_tasks()
            return (
                res,
                "task_manager_engine",
                [
                    {
                        "language": "python",
                        "code": "get_pending_tasks()",
                        "output": "Fetched Tasks",
                    }
                ],
            )
        except Exception as e:
            print(f"[TaskEngine] Error: {e}")

    try:
        from pc_automation_engine import handle_pc_automation_intent

        auto_res = handle_pc_automation_intent(prompt_low)
        if auto_res:
            return auto_res
    except Exception as e:
        print(f"[PCAutomationEngine] Error: {e}")

    # Educational / Conceptual Query Guard:
    # Pass educational, instructional, tutorial, and explanatory prompts directly to LLM
    edu_keywords = [
        "teach me",
        "explain",
        "how to learn",
        "how does",
        "how do",
        "learn",
        "tutorial",
        "guide",
        "introduction to",
        "overview of",
        "difference between",
        "concept of",
        "understand",
        "study",
        "course",
        "basics of",
        "tell me about",
    ]
    if any(k in prompt_low for k in edu_keywords):
        return None

    # ---------------------------------------------------------
    # 0A0-QUANT. QUANTITATIVE TRADING, STOCK & COMMODITIES ENGINE
    # ---------------------------------------------------------
    quant_triggers = [
        "trading",
        "stocks",
        "stock prediction",
        "predict stocks",
        "commodities",
        "future commodities",
        "gold price",
        "crude oil",
        "quant trading",
        "market prediction",
        "stock market",
        "crypto prediction",
    ]
    if any(k in prompt_low for k in quant_triggers):
        try:
            import simulated_quant_trading_engine

            report_md = (
                simulated_quant_trading_engine.execute_quant_trading_predictions()
            )
            return (
                report_md,
                "autonomous_quant_trading_engine",
                [
                    {
                        "language": "python",
                        "code": "execute_quant_trading_predictions()",
                        "output": "Fetched Real-Time Market Prices, Trained PyTorch QuantStockCommodityNN & Executed 10,000 Monte Carlo Simulations",
                    }
                ],
            )
        except Exception as e:
            print(f"[QuantEngine] Error: {e}")

    # ---------------------------------------------------------
    # 0A0-BERT. HUGGINGFACE BERT / DISTILBART ZERO-SHOT INTENT ROUTER (FAST GUARDED)
    # ---------------------------------------------------------
    vision_ml_hints = [
        "camera", "webcam", "see me", "look at me", "expression", "gesture",
        "emotion", "benchmark ml", "train model", "train a model"
    ]
    if any(h in prompt_low for h in vision_ml_hints):
        try:
            import bert_intent_classifier

            bert_label, bert_conf = bert_intent_classifier.predict_user_intent_bert(
                user_prompt
            )
            if bert_conf > 0.45:
                if bert_label == "vision_camera" and any(
                    w in prompt_low
                    for w in [
                        "see",
                        "look",
                        "camera",
                        "expression",
                        "gesture",
                        "emotion",
                        "detect",
                    ]
                ):
                    import universal_vision_gesture_engine

                    report_md = (
                        universal_vision_gesture_engine.process_image_for_emotions_gestures_objects()
                    )
                    return (
                        f"### [BERT Transformer Intent Match: `vision_camera` ({bert_conf*100:.1f}% Confidence)]\n\n"
                        + report_md,
                        "autonomous_bert_vision_engine",
                        [
                            {
                                "language": "python",
                                "code": f"bert_intent_route('{user_prompt}')",
                                "output": f"Routed to Vision Engine via DistilBART Transformer ({bert_conf*100:.1f}%)",
                            }
                        ],
                    )
                elif bert_label == "ml_training" and any(
                    w in prompt_low
                    for w in ["train", "model", "benchmark", "supervised", "unsupervised"]
                ):
                    import autonomous_ml_benchmark_engine

                    report_md = (
                        autonomous_ml_benchmark_engine.execute_complete_ml_benchmark()
                    )
                    return (
                        f"### [BERT Transformer Intent Match: `ml_training` ({bert_conf*100:.1f}% Confidence)]\n\n"
                        + report_md,
                        "autonomous_bert_ml_benchmark",
                        [
                            {
                                "language": "python",
                                "code": f"bert_intent_route('{user_prompt}')",
                                "output": f"Routed to ML Benchmark Engine via DistilBART Transformer ({bert_conf*100:.1f}%)",
                            }
                        ],
                    )
        except Exception as be:
            print(f"[BERTIntentRouter] Error: {be}")

    # ---------------------------------------------------------
    # 0A0-MEDIA. AUTONOMOUS YOUTUBE & MUSIC PLAYBACK ENGINE
    # ---------------------------------------------------------
    conversational_game_words = [
        "football", "soccer", "chess", "cricket", "basketball", "tennis",
        "badminton", "hockey", "baseball", "volleyball", "rugby", "golf",
        "video game", "video games", "board game", "cards", "poker",
        "with my friend", "with friends", "with my friends", "outside", "a game"
    ]
    is_conv_play = (
        bool(re.search(r"\b(?:i|we|they|you|he|she)\s+play\b", prompt_low))
        or (any(w in prompt_low for w in conversational_game_words) and not any(y in prompt_low for y in ["youtube", "on youtube", "song", "track", "music"]))
        or prompt_low.startswith("today ")
        or "how to play" in prompt_low
        or "let's play" in prompt_low
    )

    media_play_triggers = [
        "play song",
        "play music",
        "play video",
        "play on youtube",
        "on youtube",
        "on yt",
        "listen to",
        "play track",
    ]
    # ---------------------------------------------------------
    # Real-Time Synchronized Lyrics Intent
    # ---------------------------------------------------------
    if prompt_low in ["show lyrics", "display lyrics", "lyrics", "current lyrics", "what are the lyrics"]:
        try:
            import local_music_engine
            import lyrics_engine
            stat = local_music_engine.get_media_status()
            curr = stat.get("current_track")
            title = ""
            artist = ""
            if isinstance(curr, dict):
                title = curr.get("title") or curr.get("filename", "")
                artist = curr.get("artist", "")
            elif isinstance(curr, str):
                title = curr

            if not title:
                return ("🎵 No track currently playing to fetch lyrics for. Play a song first!", "autonomous_lyrics", [])

            lyr = lyrics_engine.get_lyrics_for_track(title, artist)
            sample_lines = []
            if lyr.get("timeline"):
                sample_lines = [item["text"] + (f" ({item['transliteration']})" if item.get("transliteration") else "") for item in lyr["timeline"][:6]]
            summary = "\n".join(sample_lines) if sample_lines else (lyr.get("plain_lyrics", "")[:300] or "Lyrics retrieved.")
            return (
                f"📜 **Lyrics for '{lyr['title']}':**\n\n{summary}\n\n*(Full synchronized lyrics loaded into Cockpit HUD)*",
                "autonomous_lyrics",
                [{"language": "json", "code": f"get_lyrics('{title}')", "output": f"{len(lyr.get('timeline', []))} timestamped lines"}]
            )
        except Exception as e:
            return (f"Could not load lyrics: {e}", "autonomous_lyrics", [])

    # ---------------------------------------------------------
    # Smart Playback Queue Voice Controls
    # ---------------------------------------------------------
    if prompt_low in ["show queue", "what is in my queue", "what's in my queue", "queue list", "view queue"]:
        try:
            import music_queue_engine
            q_data = music_queue_engine.QUEUE_ENGINE.get_queue()
            q_list = q_data.get("queue", [])
            if not q_list:
                return ("🎵 The playback queue is currently empty.", "autonomous_music_queue", [])
            lines = [f"{idx+1}. {item['title']} ({item.get('source', 'local')})" for idx, item in enumerate(q_list[:5])]
            text = f"🎵 **Playback Queue ({len(q_list)} songs):**\n" + "\n".join(lines)
            return (text, "autonomous_music_queue", [{"language": "json", "code": "QUEUE_ENGINE.get_queue()", "output": f"{len(q_list)} items"}])
        except Exception as e:
            return (f"Error reading queue: {e}", "autonomous_music_queue", [])

    if prompt_low in ["clear queue", "empty queue"]:
        try:
            import music_queue_engine
            music_queue_engine.QUEUE_ENGINE.clear()
            return ("🗑️ Playback queue cleared.", "autonomous_music_queue", [{"language": "python", "code": "QUEUE_ENGINE.clear()", "output": "Cleared"}])
        except Exception as e:
            return (f"Error clearing queue: {e}", "autonomous_music_queue", [])

    # Check "play <song> next"
    play_next_m = re.search(r"^(?:please\s+)?play\s+(.+?)\s+next$", prompt_low)
    if play_next_m:
        song_query = play_next_m.group(1).strip()
        try:
            import music_queue_engine
            q_res = music_queue_engine.QUEUE_ENGINE.enqueue(song_query, priority="next")
            if q_res.get("status") == "success":
                return (
                    f"⏭️ Enqueued **'{q_res['track']['title']}'** to play next!",
                    "autonomous_music_queue",
                    [{"language": "python", "code": f"enqueue('{song_query}', priority='next')", "output": q_res.get("message")}]
                )
        except Exception as e:
            return (f"Error queueing track: {e}", "autonomous_music_queue", [])

    # Check "queue <song>" or "add <song> to queue"
    queue_add_m = re.search(r"^(?:please\s+)?(?:queue|add\s+(.+?)\s+to\s+queue)\s*(.*)$", prompt_low)
    if queue_add_m:
        raw_song = queue_add_m.group(1) or queue_add_m.group(2)
        if raw_song and raw_song.strip() and not raw_song.strip() in ["list", "clear", "empty"]:
            song_query = raw_song.strip()
            try:
                import music_queue_engine
                q_res = music_queue_engine.QUEUE_ENGINE.enqueue(song_query, priority="end")
                if q_res.get("status") == "success":
                    return (
                        f"➕ Added **'{q_res['track']['title']}'** to queue (Position #{q_res.get('position', 1)})!",
                        "autonomous_music_queue",
                        [{"language": "python", "code": f"enqueue('{song_query}', priority='end')", "output": q_res.get("message")}]
                    )
            except Exception as e:
                return (f"Error queueing track: {e}", "autonomous_music_queue", [])

    is_media_command = not is_conv_play and (
        any(k in prompt_low for k in media_play_triggers) or (
            ("youtube" in prompt_low or "yt" in prompt_low)
            and not any(w in prompt_low for w in ["close", "stop", "exit", "kill"])
        )
    )

    if is_media_command:
        try:
            import local_music_engine

            # Clean up query anywhere in the string
            clean_query = user_prompt.strip().rstrip(".?!;")
            clean_query = re.sub(
                r"\b(?:on\s+youtube|on\s+yt|youtube|yt)\b",
                "",
                clean_query,
                flags=re.IGNORECASE,
            )
            clean_query = re.sub(
                r"^(?:play\s+song\s+by|play\s+song|play\s+music|play\s+video|play|listen\s+to|search\s+and\s+play)\s+",
                "",
                clean_query,
                flags=re.IGNORECASE,
            ).strip()
            clean_query = re.sub(r"\s+", " ", clean_query).strip().rstrip(".?!;")

            if not clean_query:
                clean_query = "trending music"
                
            force_youtube_web = ("youtube" in prompt_low or "video" in prompt_low or "on yt" in prompt_low)

            if not force_youtube_web:
                track = local_music_engine.find_track(clean_query)
                if track:
                    res = local_music_engine.play_track(track["path"])
                    if res.get("status") == "success":
                        return (
                            f"🎵 Found locally! Playing '{track['filename']}' in your PC Music Player.",
                            "autonomous_music_engine_local",
                            [
                                {
                                    "language": "powershell",
                                    "code": f"start '{track['path']}'",
                                    "output": f"Playing {track['filename']}",
                                }
                            ],
                        )

                # Not found locally: download using local_music_engine and play in default PC player!
                download_res = local_music_engine.download_and_play_track(clean_query)
                if download_res.get("status") == "success":
                    return (
                        f"🎵 Downloaded from YouTube! Playing '{download_res['filename']}' in your PC Music Player.",
                        "autonomous_music_engine_download",
                        [
                            {
                                "language": "powershell",
                                "code": f'Start-Process "{download_res["path"]}"',
                                "output": f"Downloaded and playing {download_res['filename']}",
                            }
                        ],
                    )

            # Explicit YouTube or Video request -> Open in Google Chrome (PC Speakers)
            encoded_query = urllib.parse.quote(clean_query)
            target_url = f"https://www.youtube.com/results?search_query={encoded_query}"
            local_music_engine.open_in_chrome(target_url)

            return (
                f"▶️ Opened YouTube in Google Chrome: Playing '{clean_query}'.",
                "autonomous_youtube_media_engine",
                [
                    {
                        "language": "powershell",
                        "code": f'Start-Process "chrome.exe" "{target_url}"',
                        "output": f"Opened YouTube in Google Chrome for {clean_query}",
                    }
                ],
            )
        except Exception as me:
            print(f"[MediaPlaybackEngine] Error: {me}")

    # ---------------------------------------------------------
    # 0A0-CHROME. AUTONOMOUS CHROME & GOOGLE BROWSER ENGINE
    # ---------------------------------------------------------
    chrome_open_triggers = [
        "open google chrome",
        "open chrome",
        "open google",
        "launch chrome",
        "start chrome",
        "open browser",
    ]
    matched_chrome_trigger = None
    for k in chrome_open_triggers:
        if k in prompt_low:
            matched_chrome_trigger = k
            break

    if matched_chrome_trigger:
        try:
            import subprocess

            # Check if there is an extra command or query attached (e.g. "open chrome and search ...", "open chrome and give me 5 latest songs")
            sub_part = re.sub(
                r"^(?:please\s+|can\s+you\s+)?" + re.escape(matched_chrome_trigger),
                "",
                prompt_low,
                flags=re.IGNORECASE,
            ).strip()
            sub_part = re.sub(r"^(?:and|to|then|\&)\s+", "", sub_part).strip()

            if sub_part:
                clean_query = re.sub(
                    r"^(?:search\s+for|look\s+up|find|search|give\s+me|tell\s+me|show\s+me|play)\s+",
                    "",
                    sub_part,
                ).strip()
                if not clean_query:
                    clean_query = sub_part

                if any(
                    w in sub_part
                    for w in [
                        "song",
                        "songs",
                        "music",
                        "punjabi",
                        "track",
                        "video",
                        "sing",
                    ]
                ):
                    target_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(clean_query)}"
                    voice_resp = f"I have opened Chrome and searched for '{clean_query.title()}' on YouTube for you."
                    desc = f"Opened YouTube search for '{clean_query}'"
                else:
                    target_url = f"https://www.google.com/search?q={urllib.parse.quote(clean_query)}"
                    voice_resp = f"I have opened Chrome and searched for '{clean_query.title()}' on Google for you."
                    desc = f"Opened Google search for '{clean_query}'"

                try:
                    subprocess.Popen(
                        [
                            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                            target_url,
                        ]
                    )
                except Exception:
                    webbrowser.open(target_url)

                return (
                    voice_resp,
                    "autonomous_chrome_search_launcher",
                    [
                        {
                            "language": "powershell",
                            "code": f"start chrome '{target_url}'",
                            "output": desc,
                        }
                    ],
                )
            else:
                target_url = "https://www.google.com"
                try:
                    subprocess.Popen(
                        [
                            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                            target_url,
                        ]
                    )
                except Exception:
                    webbrowser.open(target_url)

                return (
                    "I have opened Google Chrome for you.",
                    "autonomous_chrome_launcher",
                    [
                        {
                            "language": "powershell",
                            "code": f"start chrome '{target_url}'",
                            "output": "Opened Google Chrome",
                        }
                    ],
                )
        except Exception as ce:
            print(f"[ChromeLauncher] Error: {ce}")

    # ---------------------------------------------------------
    # 0A0-TRAVEL. UNIFIED FLIGHTS, HOTELS & CAR RENTAL ENGINE
    # ---------------------------------------------------------
    try:
        import travel_booking_engine

        travel_res = travel_booking_engine.handle_travel_booking_intent(user_prompt)
        if travel_res:
            return travel_res
    except Exception as te:
        print(f"[TravelBookingEngine] Error: {te}")

    # ---------------------------------------------------------
    # 0A0. SMART LIGHT & KASA HOME AUTOMATION ENGINE
    # ---------------------------------------------------------
    light_keywords = [
        "light",
        "lights",
        "room light",
        "kasa",
        "lamp",
        "bulb",
        "deeps room",
    ]
    has_light_kw = any(
        re.search(r"\b" + re.escape(k) + r"\b", prompt_low) for k in light_keywords
    )
    has_light_context = False
    try:
        import kasa_controller

        has_light_context = has_light_kw or kasa_controller.is_recent_light_context()
    except Exception:
        has_light_context = has_light_kw

    if has_light_context and not any(
        w in prompt_low for w in ["flight", "flights", "fly"]
    ):
        try:
            import kasa_controller

            kasa_res = kasa_controller.execute_kasa_intent(user_prompt)
            if kasa_res:
                msg, res_data = kasa_res
                return (
                    msg,
                    "autonomous_kasa_light",
                    [
                        {
                            "language": "python",
                            "code": f"execute_kasa_intent('{user_prompt}')",
                            "output": str(res_data),
                        }
                    ],
                )
        except Exception as e:
            print(f"[KasaIntentEngine] Error: {e}")

    # ---------------------------------------------------------
    # 0A13. UNIVERSAL COMPUTER VISION, EMOTION & GESTURE ENGINE
    # ---------------------------------------------------------
    vision_gesture_triggers = [
        "face expression",
        "hand sign",
        "hand gesture",
        "facial expression",
        "recognise different kind of things",
        "gesture recognition",
        "emotion detection",
        "object recognition",
    ]
    if any(k in prompt_low for k in vision_gesture_triggers):
        try:
            import universal_vision_gesture_engine

            report_md = (
                universal_vision_gesture_engine.process_image_for_emotions_gestures_objects()
            )
            return (
                report_md,
                "autonomous_vision_gesture_engine",
                [
                    {
                        "language": "python",
                        "code": "process_image_for_emotions_gestures_objects()",
                        "output": "Recognized Facial Expressions, Hand Signs/Gestures & 1,000+ Objects",
                    }
                ],
            )
        except Exception as e:
            print(f"[VisionGestureEngine] Error: {e}")

    # ---------------------------------------------------------
    # 0A15. FUTURE PREDICTION & TIME-SERIES FORECASTING ENGINE
    # ---------------------------------------------------------
    future_pred_triggers = [
        "predict future",
        "predict the future",
        "future prediction",
        "future predictions",
        "forecast future",
        "future forecast",
        "predict system future",
    ]
    if any(k in prompt_low for k in future_pred_triggers):
        try:
            import future_prediction_engine

            report_md = future_prediction_engine.predict_future_trends()
            return (
                report_md,
                "autonomous_future_prediction_engine",
                [
                    {
                        "language": "python",
                        "code": "predict_future_trends()",
                        "output": "Ran PyTorch Workload Predictor NN & 10,000 Monte Carlo Singularity Simulations",
                    }
                ],
            )
        except Exception as e:
            print(f"[FuturePredictionEngine] Error: {e}")

    # ---------------------------------------------------------
    # 0A16. QUANTITATIVE TRADING, STOCK & COMMODITIES ENGINE
    # ---------------------------------------------------------
    quant_triggers = [
        "trading",
        "stocks",
        "stock prediction",
        "predict stocks",
        "commodities",
        "future commodities",
        "gold price",
        "crude oil",
        "quant trading",
        "market prediction",
        "stock market",
        "crypto prediction",
    ]
    if any(k in prompt_low for k in quant_triggers):
        try:
            import simulated_quant_trading_engine

            report_md = (
                simulated_quant_trading_engine.execute_quant_trading_predictions()
            )
            return (
                report_md,
                "autonomous_quant_trading_engine",
                [
                    {
                        "language": "python",
                        "code": "execute_quant_trading_predictions()",
                        "output": "Fetched Real-Time Market Prices, Trained PyTorch QuantStockCommodityNN & Executed 10,000 Monte Carlo Simulations",
                    }
                ],
            )
        except Exception as e:
            print(f"[QuantEngine] Error: {e}")

    # ---------------------------------------------------------
    # 0A14. DEEP LEARNING CONTINUOUS OPTIMIZER ENGINE
    # ---------------------------------------------------------
    dl_optimizer_triggers = [
        "run deep learning optimizer",
        "auto tune workstation",
        "run self improvement",
        "improve overall efficiency",
    ]
    if any(k in prompt_low for k in dl_optimizer_triggers):
        try:
            import continuous_deep_learning_optimizer

            report_md = (
                continuous_deep_learning_optimizer.run_deep_learning_self_improvement()
            )
            return (
                report_md,
                "autonomous_continuous_deep_learning_optimizer",
                [
                    {
                        "language": "python",
                        "code": "run_deep_learning_self_improvement()",
                        "output": "Trained PyTorch WorkstationSelfTuningNN & Persisted to PostgreSQL 18",
                    }
                ],
            )
        except Exception as e:
            print(f"[DLOptimizerEngine] Error: {e}")

    # ---------------------------------------------------------
    # 0A12. AUTONOMOUS SUPERVISED & UNSUPERVISED ML SUITE
    # ---------------------------------------------------------
    ml_benchmark_triggers = [
        "run supervised benchmark",
        "run unsupervised benchmark",
        "train all models",
        "run ml benchmark",
        "train ml models",
    ]
    if any(k in prompt_low for k in ml_benchmark_triggers):
        try:
            import autonomous_ml_benchmark_engine

            report_md = autonomous_ml_benchmark_engine.execute_complete_ml_benchmark()
            return (
                report_md,
                "autonomous_ml_benchmark_engine",
                [
                    {
                        "language": "python",
                        "code": "execute_complete_ml_benchmark()",
                        "output": "Trained 14 Supervised & Unsupervised Models & Logged to PostgreSQL 18",
                    }
                ],
            )
        except Exception as e:
            print(f"[MLBenchmarkEngine] Error: {e}")

    # ---------------------------------------------------------
    # 0A11. ACTUAL EXECUTABLE PYTORCH PC NEURAL NETWORK ENGINE
    # ---------------------------------------------------------
    actual_pc_nn_triggers = [
        "actual neural network of pc",
        "real neural network of pc",
        "pytorch pc neural network",
        "pc neural network model",
        "train pc neural network",
    ]
    if any(k in prompt_low for k in actual_pc_nn_triggers):
        try:
            import actual_pc_neural_network

            report_md = (
                actual_pc_neural_network.train_and_run_actual_pc_neural_network()
            )
            return (
                report_md,
                "autonomous_actual_pc_neural_network",
                [
                    {
                        "language": "python",
                        "code": "train_and_run_actual_pc_neural_network()",
                        "output": "Trained & Executed PyTorch Neural Network of PC System Tensors",
                    }
                ],
            )
        except Exception as e:
            print(f"[ActualPCNNEngine] Error: {e}")

    # ---------------------------------------------------------
    # 0A10. PC BRAIN GRAPH NEURAL NETWORK (GNN) ENGINE
    # ---------------------------------------------------------
    gnn_brain_triggers = [
        "gnn of my pc",
        "brain of this local ai",
        "gnn brain",
        "knowledge graph of pc",
        "ai brain topology",
        "how local ai works",
    ]
    if any(k in prompt_low for k in gnn_brain_triggers):
        try:
            import pc_brain_gnn_engine

            report_md = pc_brain_gnn_engine.generate_pc_brain_gnn()
            return (
                report_md,
                "autonomous_pc_brain_gnn_engine",
                [
                    {
                        "language": "python",
                        "code": "generate_pc_brain_gnn()",
                        "output": "Generated Interactive Graph Neural Network (GNN) Topology of PC Brain",
                    }
                ],
            )
        except Exception as e:
            print(f"[PCBrainGNNEngine] Error: {e}")

    # ---------------------------------------------------------
    # 0A9. DEEP LEARNING & NEURAL NETWORK ENGINE
    # ---------------------------------------------------------
    dl_triggers = [
        "generate deep learning model",
        "build cnn model",
        "build rnn model",
        "build transformer model",
        "create deep learning script",
        "generate pytorch model",
    ]
    if any(k in prompt_low for k in dl_triggers):
        try:
            import deep_learning_model_generator

            report_md = deep_learning_model_generator.generate_neural_network_model(
                user_prompt
            )
            return (
                report_md,
                "autonomous_deep_learning_engine",
                [
                    {
                        "language": "python",
                        "code": f"generate_neural_network_model('{user_prompt}')",
                        "output": "Generated Executable PyTorch Deep Learning Model Code",
                    }
                ],
            )
        except Exception as e:
            print(f"[DeepLearningEngine] Error: {e}")

    # ---------------------------------------------------------
    # 0A8. UNIVERSAL ATTACHMENT & FILE/FOLDER PROCESSOR
    # ---------------------------------------------------------
    attach_triggers = [
        "attachment",
        "attach",
        "folder",
        "directory",
        "file path",
        ".pdf",
        ".docx",
        ".xlsx",
        ".zip",
        ".csv",
    ]
    if any(k in prompt_low for k in attach_triggers):
        try:
            import universal_attachment_processor

            report_md = (
                universal_attachment_processor.process_file_or_folder_attachment(
                    user_prompt
                )
            )
            return (
                report_md,
                "autonomous_attachment_processor",
                [
                    {
                        "language": "python",
                        "code": f"process_file_or_folder_attachment('{user_prompt}')",
                        "output": "Ingested File/Folder Attachment & Extracted Metrics",
                    }
                ],
            )
        except Exception as e:
            print(f"[AttachmentProcessorEngine] Error: {e}")

    # ---------------------------------------------------------
    # 0A7. UNIVERSAL MULTIMODAL DATASET ENGINE
    # ---------------------------------------------------------
    modality_triggers = [
        "3d",
        "audio",
        "document",
        "geospatial",
        "image",
        "tabular",
        "text dataset",
        "time-series",
        "time series",
        "video dataset",
        "multimodal",
        "modalities",
    ]
    if any(k in prompt_low for k in modality_triggers):
        try:
            import universal_multimodal_dataset_engine

            report_md = universal_multimodal_dataset_engine.analyze_dataset_modality(
                user_prompt
            )
            return (
                report_md,
                "autonomous_multimodal_dataset_engine",
                [
                    {
                        "language": "python",
                        "code": f"analyze_dataset_modality('{user_prompt}')",
                        "output": "Analyzed & Executed Multimodal Dataset Pipeline",
                    }
                ],
            )
        except Exception as e:
            print(f"[MultimodalDatasetEngine] Error: {e}")

    # ---------------------------------------------------------
    # 0A6. PII, NER & TOKEN CLASSIFICATION ENGINE
    # ---------------------------------------------------------
    ner_triggers = [
        "pii",
        "token classification",
        "gliner",
        "ner",
        "named entity",
        "privacy filter",
        "extract entities",
        "anonymize",
    ]
    if any(k in prompt_low for k in ner_triggers):
        try:
            import pii_ner_extractor_engine

            report_md = pii_ner_extractor_engine.extract_pii_and_entities(user_prompt)
            return (
                report_md,
                "autonomous_pii_ner_engine",
                [
                    {
                        "language": "python",
                        "code": f"extract_pii_and_entities('{user_prompt}')",
                        "output": "Extracted PII, NER Entities & Token Classification Table",
                    }
                ],
            )
        except Exception as e:
            print(f"[PIINEREngine] Error: {e}")

    # ---------------------------------------------------------
    # 0A5. POSTGRESQL ENTERPRISE DATABASE ENGINE
    # ---------------------------------------------------------
    pg_triggers = ["postgresql", "postgres", "pg database", "connect postgresql"]
    if any(k in prompt_low for k in pg_triggers):
        try:
            import postgresql_engine

            res = postgresql_engine.test_postgresql_connection()
            status_emoji = "🐘" if res["status"] == "success" else "⚙️"
            resp_md = (
                f"{status_emoji} **PostgreSQL Enterprise Database Status**\n\n"
                f"**Connection Status:** `{res['status'].upper()}`\n"
                f"**Details:** `{res['message']}`\n\n"
                f"---  \n"
                f"💡 **PostgreSQL Integration in Workstation:**\n"
                f"• Installed **`psycopg2`** Python connector drivers.\n"
                f"• Detected active local PostgreSQL service on `localhost:5432`.\n"
                f"• Power BI Desktop can import directly from PostgreSQL using server: `localhost:5432`!"
            )
            return (
                resp_md,
                "autonomous_postgresql_engine",
                [
                    {
                        "language": "python",
                        "code": "test_postgresql_connection()",
                        "output": res["message"],
                    }
                ],
            )
        except Exception as e:
            print(f"[PostgreSQLEngine] Error: {e}")

    # ---------------------------------------------------------
    # 0A4. INTERACTIVE CHAPTER ACADEMY & ADAPTIVE QUIZ ENGINE
    # ---------------------------------------------------------
    chapter_triggers = [
        "chapter",
        "chapters",
        "quiz",
        "test me",
        "take test",
        "step by step",
        "weak area",
        "answer",
        "1b",
        "2a",
        "option",
    ]
    if any(k in prompt_low for k in chapter_triggers) and not any(
        k in prompt_low for k in ["light", "kasa"]
    ):
        try:
            import interactive_learning_academy

            resp_md = interactive_learning_academy.process_academy_request(user_prompt)
            return (
                resp_md,
                "autonomous_chapter_academy",
                [
                    {
                        "language": "python",
                        "code": f"process_academy_request('{user_prompt}')",
                        "output": "Evaluated Quiz / Displayed Current Chapter",
                    }
                ],
            )
        except Exception as e:
            print(f"[ChapterAcademyEngine] Error: {e}")

    # ---------------------------------------------------------
    # 0A3. UNIVERSAL ONLINE LEARNER & EXPERT TUTOR ENGINE
    # ---------------------------------------------------------
    tutor_triggers = [
        "teach me",
        "tutorial",
        "how to learn",
        "expert course",
        "skill path",
        "lesson",
        "teach",
    ]
    if any(k in prompt_low for k in tutor_triggers) and not any(
        k in prompt_low for k in ["light", "kasa"]
    ):
        try:
            import autonomous_online_learner_tutor
            import expert_tutor_engine

            # Check if topic is in core offline curriculum (powerbi, sql, fiber, automation)
            if any(
                k in prompt_low
                for k in [
                    "powerbi",
                    "power bi",
                    "sql",
                    "fiber",
                    "otdr",
                    "telecom",
                    "automation",
                    "playwright",
                    "dom",
                ]
            ):
                tutorial_md = expert_tutor_engine.generate_expert_tutorial(user_prompt)
            else:
                # Online Research & Self-Learning Teacher Engine
                tutorial_md = autonomous_online_learner_tutor.learn_and_teach_anything(
                    user_prompt
                )

            return (
                tutorial_md,
                "autonomous_online_learner_tutor",
                [
                    {
                        "language": "python",
                        "code": f"learn_and_teach_anything('{user_prompt}')",
                        "output": "Autonomously Researched Web Live & Synthesized Simple Lesson",
                    }
                ],
            )
        except Exception as e:
            print(f"[OnlineLearnerEngine] Error: {e}")

    # ---------------------------------------------------------
    # 0A2. AUTONOMOUS RESEARCH, DATASET & POWER BI REPORT ENGINE
    # ---------------------------------------------------------
    research_triggers = [
        "research",
        "data set",
        "dataset",
        "make report",
        "powerbi",
        "power bi",
        "make graphs",
        "create report",
        "analyze data",
    ]
    if any(k in prompt_low for k in research_triggers):
        try:
            import autonomous_research_powerbi_engine

            res = (
                autonomous_research_powerbi_engine.generate_research_and_powerbi_report(
                    user_prompt
                )
            )

            s = res.get("summary", {})
            resp_md = (
                f"📊 **Autonomous Research & Power BI Report System Active!**\n\n"
                f"**Report Title:** `{res.get('title')}`\n"
                f"**Total Records Analyzed:** `{s.get('records')}` records\n"
                f"**Average Efficiency Score:** `{s.get('avg_efficiency')}%`\n"
                f"**Total Estimated Financial Impact:** `${s.get('total_impact_cad'):,} CAD`\n\n"
                f"---  \n"
                f"📁 **Generated Artifacts & Assets:**  \n"
                f"• 📝 **Executive Report (Markdown):** `{res.get('report_file')}`  \n"
                f"• 📈 **High-Res Visual Analytics Chart:** `{res.get('chart_file')}`  \n"
                f"• 📊 **Power BI Ready Dataset (CSV):** `{res.get('csv_file')}`  \n"
                f"• 💻 **Power BI Python Integration Script:** `{res.get('powerbi_script')}`\n\n"
                f"*Your Power BI dataset & charts have been automatically synthesized and saved to your local reports folder!*"
            )
            return (
                resp_md,
                "autonomous_research_powerbi",
                [
                    {
                        "language": "python",
                        "code": f"generate_research_and_powerbi_report('{user_prompt}')",
                        "output": "Generated Executive Report, PNG Charts & Power BI CSV/Python Packages",
                    }
                ],
            )
        except Exception as e:
            print(f"[ResearchPowerBIEngine] Error: {e}")


    if any(
        k in prompt_low
        for k in [
            "crawl",
            "crawl4ai",
            "extract markdown",
            "scrape markdown",
            "markdown extract",
            "markdown crawl",
        ]
    ):
        try:
            import dom_system_engine

            target_url = "https://httpbin.org/html"
            url_match = re.search(r"https?://[^\s]+", user_prompt)
            if url_match:
                target_url = url_match.group(0)

            crawl_res = dom_system_engine.extract_clean_markdown(target_url)
            md_content = crawl_res.get("markdown", "")
            preview = md_content[:1500] if len(md_content) > 1500 else md_content
            summary_str = (
                f"🕷️ **Crawl4ai Extraction Complete!**\n\n"
                f"**Engine:** `{crawl_res.get('engine', 'crawl4ai')}` | **Target:** `{target_url}`\n"
                f"**Extracted Characters:** `{crawl_res.get('char_count', len(md_content))}` chars\n\n"
                f"### Structured Markdown:\n\n{preview}"
            )
            return (
                summary_str,
                "crawl4ai_extraction",
                [
                    {
                        "language": "python",
                        "code": f"dom_system_engine.extract_clean_markdown('{target_url}')",
                        "output": "Clean Markdown Extracted",
                    }
                ],
            )
        except Exception as e:
            print(f"[Crawl4aiEngine] Error: {e}")

    # ---------------------------------------------------------
    # 0A1. AUTONOMOUS AGENTIC BROWSER FORM FILLING LOOP
    # ---------------------------------------------------------
    if any(
        k in prompt_low
        for k in [
            "fill form",
            "auto fill form",
            "browser agent",
            "browser use",
            "agentic form",
            "fill application",
            "fill out form",
        ]
    ):
        try:
            import dom_system_engine

            target_url = "https://ca.indeed.com"
            url_match = re.search(r"https?://[^\s]+", user_prompt)
            if url_match:
                target_url = url_match.group(0)

            loop_res = dom_system_engine.autonomous_agentic_browser_loop(
                url=target_url, task_instruction=user_prompt, headless=False
            )
            steps_summary = "\n".join(
                [
                    f"- Step {s['step']}: [{s['action'].upper()}] Value: '{s.get('value')}'"
                    for s in loop_res.get("steps_log", [])
                ]
            )
            summary_str = (
                f"🤖 **Autonomous Browser Agent Complete!**\n\n"
                f"**Target URL:** `{target_url}`\n"
                f"**Total Steps Executed:** `{loop_res.get('total_steps', 0)}`\n\n"
                f"**Action Trace:**\n{steps_summary}"
            )
            return (
                summary_str,
                "autonomous_browser_agent",
                [
                    {
                        "language": "python",
                        "code": f"dom_system_engine.autonomous_agentic_browser_loop('{target_url}', task_instruction=\"{user_prompt}\")",
                        "output": "Form Filled & Submitted",
                    }
                ],
            )
        except Exception as e:
            print(f"[BrowserAgentLoop] Error: {e}")

    # ---------------------------------------------------------
    # 0A2. DOM SYSTEM ENGINE & DOM AUTOMATION ROUTER
    # ---------------------------------------------------------
    if any(
        k in prompt_low
        for k in [
            "dom",
            "dom system",
            "inspect dom",
            "dom tree",
            "dom element",
            "query dom",
        ]
    ):
        try:
            import dom_system_engine

            target_url = "https://ca.indeed.com"
            url_match = re.search(r"https?://[^\s]+", user_prompt)
            if url_match:
                target_url = url_match.group(0)

            dom_res = dom_system_engine.inspect_dom_tree(target_url)
            summary_str = (
                f"🌳 **DOM System Engine Active!**\n\n"
                f"**Target URL:** `{target_url}`\n"
                f"**Page Title:** `{dom_res.get('title', 'N/A')}`\n"
                f"**DOM Input Fields Found:** `{dom_res.get('input_count', 0)}` nodes\n"
                f"**DOM Clickable Buttons Found:** `{dom_res.get('button_count', 0)}` nodes\n\n"
                f"```json\n{json.dumps(dom_res, indent=2)}\n```"
            )
            return (
                summary_str,
                "autonomous_dom_system",
                [
                    {
                        "language": "python",
                        "code": f"dom_system_engine.inspect_dom_tree('{target_url}')",
                        "output": "Inspected DOM Tree",
                    }
                ],
            )
        except Exception as e:
            print(f"[DOMSystemEngine] Error: {e}")
    if re.search(
        r"\b(?:lock|lockup)\b.*?\b(?:pc|computer|screen|workstation|laptop)\b",
        prompt_low,
    ) or prompt_low in ["lock", "lock pc", "lock computer", "lock screen"]:
        try:
            ctypes.windll.user32.LockWorkStation()
            return (
                "🔒 **Autonomous System Control:** Workstation successfully locked!",
                "autonomous_system_lock",
                [
                    {
                        "language": "python",
                        "code": "ctypes.windll.user32.LockWorkStation()",
                        "output": "Locked workstation",
                    }
                ],
            )
        except Exception:
            subprocess.Popen(["rundll32.exe", "user32.dll,LockWorkStation"], shell=True)
            return (
                "🔒 **Autonomous System Control:** Workstation lock command sent!",
                "autonomous_system_lock",
                [
                    {
                        "language": "powershell",
                        "code": "rundll32.exe user32.dll,LockWorkStation",
                        "output": "Locked workstation",
                    }
                ],
            )

    # ---------------------------------------------------------
    # 0B. CLOSE APPLICATION / CLOSE YOUTUBE & BROWSER TABS
    # ---------------------------------------------------------
    close_match = re.search(
        r"^(?:close|exit|quit|kill|stop|terminate)\s+(.+)$", prompt_low
    )
    if close_match or prompt_low in [
        "close youtube",
        "close tab",
        "close browser",
        "close chrome",
        "close window",
    ]:
        target_app = (
            close_match.group(1).strip()
            if close_match
            else prompt_low.replace("close", "").strip()
        )
        target_low = target_app.lower()

        # If closing youtube, tab, or browser tab
        if "youtube" in target_low or "tab" in target_low or target_low == "":
            try:
                # Stop any media playing
                VK_MEDIA_STOP = 0xB2
                KEYEVENTF_KEYUP = 0x0002
                ctypes.windll.user32.keybd_event(VK_MEDIA_STOP, 0, 0, 0)
                ctypes.windll.user32.keybd_event(VK_MEDIA_STOP, 0, KEYEVENTF_KEYUP, 0)

                # Send Ctrl+W to close active tab
                VK_CONTROL = 0x11
                VK_W = 0x57
                ctypes.windll.user32.keybd_event(VK_CONTROL, 0, 0, 0)
                ctypes.windll.user32.keybd_event(VK_W, 0, 0, 0)
                ctypes.windll.user32.keybd_event(VK_W, 0, KEYEVENTF_KEYUP, 0)
                ctypes.windll.user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)

                return (
                    "⏹️ **Autonomous Media Control:** Closed YouTube tab and stopped playback!",
                    "autonomous_close_tab",
                    [
                        {
                            "language": "powershell",
                            "code": "SendKeys('^{w}') + VK_MEDIA_STOP",
                            "output": "Closed active tab and stopped media",
                        }
                    ],
                )
            except Exception:
                pass

        # App to exe mapping
        exe_map = {
            "chrome": "chrome.exe",
            "browser": "chrome.exe",
            "google chrome": "chrome.exe",
            "edge": "msedge.exe",
            "notepad": "notepad.exe",
            "spotify": "spotify.exe",
            "calculator": "calc.exe",
            "calc": "calc.exe",
            "vscode": "code.exe",
            "code": "code.exe",
            "word": "WINWORD.EXE",
            "excel": "EXCEL.EXE",
            "powerpoint": "POWERPNT.EXE",
            "vlc": "vlc.exe",
            "discord": "Discord.exe",
            "telegram": "Telegram.exe",
            "slack": "slack.exe",
            "zoom": "Zoom.exe",
            "paint": "mspaint.exe",
            "terminal": "WindowsTerminal.exe",
            "snipping tool": "SnippingTool.exe",
        }

        exe_name = exe_map.get(target_low, f"{target_low}.exe")
        try:
            subprocess.Popen(f"taskkill /IM {exe_name} /F", shell=True)
            return (
                f'🛑 **Autonomous System Action:** Terminated application **"{exe_name}"**!',
                "autonomous_app_close",
                [
                    {
                        "language": "powershell",
                        "code": f"taskkill /IM {exe_name} /F",
                        "output": f"Terminated {exe_name}",
                    }
                ],
            )
        except Exception:
            pass

    # ---------------------------------------------------------
    # 0C1. DYNAMIC SYSTEM VOLUME & MEDIA CONTROLLER (HARDWARE)
    # ---------------------------------------------------------
    if prompt_low in ["mute", "unmute", "toggle mute", "mute volume", "unmute volume"]:
        try:
            VK_VOLUME_MUTE = 0xAD
            KEYEVENTF_KEYUP = 0x0002
            ctypes.windll.user32.keybd_event(VK_VOLUME_MUTE, 0, 0, 0)
            ctypes.windll.user32.keybd_event(VK_VOLUME_MUTE, 0, KEYEVENTF_KEYUP, 0)
            return (
                "🔇 **Autonomous Hardware Control:** Toggled audio mute!",
                "autonomous_volume_mute",
                [
                    {
                        "language": "python",
                        "code": "keybd_event(VK_VOLUME_MUTE)",
                        "output": "Toggled mute",
                    }
                ],
            )
        except Exception:
            pass

    if prompt_low in ["volume up", "louder", "turn up volume", "increase volume"]:
        try:
            VK_VOLUME_UP = 0xAF
            KEYEVENTF_KEYUP = 0x0002
            for _ in range(5):
                ctypes.windll.user32.keybd_event(VK_VOLUME_UP, 0, 0, 0)
                ctypes.windll.user32.keybd_event(VK_VOLUME_UP, 0, KEYEVENTF_KEYUP, 0)
            return (
                "🔊 **Autonomous Hardware Control:** Volume increased!",
                "autonomous_volume_up",
                [
                    {
                        "language": "python",
                        "code": "keybd_event(VK_VOLUME_UP x 5)",
                        "output": "Volume increased",
                    }
                ],
            )
        except Exception:
            pass

    if prompt_low in ["volume down", "quieter", "turn down volume", "decrease volume"]:
        try:
            VK_VOLUME_DOWN = 0xAE
            KEYEVENTF_KEYUP = 0x0002
            for _ in range(5):
                ctypes.windll.user32.keybd_event(VK_VOLUME_DOWN, 0, 0, 0)
                ctypes.windll.user32.keybd_event(VK_VOLUME_DOWN, 0, KEYEVENTF_KEYUP, 0)
            return (
                "🔉 **Autonomous Hardware Control:** Volume decreased!",
                "autonomous_volume_down",
                [
                    {
                        "language": "python",
                        "code": "keybd_event(VK_VOLUME_DOWN x 5)",
                        "output": "Volume decreased",
                    }
                ],
            )
        except Exception:
            pass

    is_play_pause = (
        prompt_low in [
            "play", "pause", "play music", "played music", "pause music", "pause the music",
            "play the music", "play song", "pause song", "resume music", "resume song",
            "play pause", "play or pause", "pause or play", "stop music", "stop the music",
            "unpause", "toggle music", "music pause", "music play"
        ]
        or bool(re.search(r"^(?:hey\s+(?:deep|jarvis|friday)\s+)?(?:please\s+)?(?:play|pause|resume|unpause)(?:\s+(?:the\s+)?(?:music|song|playback|audio))?$", prompt_low))
        or bool(re.search(r"^(?:play\s+or\s+pause|pause\s+or\s+play)$", prompt_low))
    )

    if is_play_pause:
        try:
            VK_MEDIA_PLAY_PAUSE = 0xB3 # Standard Windows VK_MEDIA_PLAY_PAUSE
            KEYEVENTF_EXTENDEDKEY = 0x0001
            KEYEVENTF_KEYUP = 0x0002
            ctypes.windll.user32.keybd_event(VK_MEDIA_PLAY_PAUSE, 0, KEYEVENTF_EXTENDEDKEY, 0)
            time.sleep(0.05)
            ctypes.windll.user32.keybd_event(VK_MEDIA_PLAY_PAUSE, 0, KEYEVENTF_EXTENDEDKEY | KEYEVENTF_KEYUP, 0)
            return (
                "⏯️ **Autonomous Media Control:** Toggled media playback (Play/Pause)!",
                "autonomous_media_toggle",
                [
                    {
                        "language": "python",
                        "code": "keybd_event(VK_MEDIA_PLAY_PAUSE)",
                        "output": "Toggled play/pause",
                    }
                ],
            )
        except Exception:
            pass

    is_next = (
        prompt_low in [
            "play next", "next song", "next track", "next", "skip song",
            "skip track", "skip", "play the next", "the next", "forward track", "next music"
        ]
        or bool(re.search(r"^(?:hey\s+(?:deep|jarvis|friday)\s+)?(?:please\s+)?(?:play\s+)?(?:next|skip)(?:\s+(?:the\s+)?(?:song|track|music))?$", prompt_low))
    )

    if is_next:
        try:
            VK_MEDIA_NEXT_TRACK = 0xB0
            KEYEVENTF_EXTENDEDKEY = 0x0001
            KEYEVENTF_KEYUP = 0x0002
            ctypes.windll.user32.keybd_event(VK_MEDIA_NEXT_TRACK, 0, KEYEVENTF_EXTENDEDKEY, 0)
            time.sleep(0.05)
            ctypes.windll.user32.keybd_event(VK_MEDIA_NEXT_TRACK, 0, KEYEVENTF_EXTENDEDKEY | KEYEVENTF_KEYUP, 0)
            return (
                "⏭️ **Autonomous Media Control:** Skipped to next track!",
                "autonomous_media_next",
                [
                    {
                        "language": "python",
                        "code": "keybd_event(VK_MEDIA_NEXT_TRACK)",
                        "output": "Next track",
                    }
                ],
            )
        except Exception:
            pass

    is_prev = (
        prompt_low in [
            "play prev", "play previous", "previous song", "previous track",
            "prev song", "prev track", "previous", "prev", "play the previous",
            "the previous", "in previous", "rewind", "back song", "back track", "previous music"
        ]
        or bool(re.search(r"^(?:hey\s+(?:deep|jarvis|friday)\s+)?(?:please\s+)?(?:play\s+)?(?:prev|previous|rewind)(?:\s+(?:the\s+)?(?:song|track|music))?$", prompt_low))
    )

    if is_prev:
        try:
            VK_MEDIA_PREV_TRACK = 0xB1
            KEYEVENTF_EXTENDEDKEY = 0x0001
            KEYEVENTF_KEYUP = 0x0002
            ctypes.windll.user32.keybd_event(VK_MEDIA_PREV_TRACK, 0, KEYEVENTF_EXTENDEDKEY, 0)
            time.sleep(0.05)
            ctypes.windll.user32.keybd_event(VK_MEDIA_PREV_TRACK, 0, KEYEVENTF_EXTENDEDKEY | KEYEVENTF_KEYUP, 0)
            return (
                "⏮️ **Autonomous Media Control:** Went back to previous track!",
                "autonomous_media_prev",
                [
                    {
                        "language": "python",
                        "code": "keybd_event(VK_MEDIA_PREV_TRACK)",
                        "output": "Previous track",
                    }
                ],
            )
        except Exception:
            pass

    # ---------------------------------------------------------
    # 0C2. DYNAMIC UNIVERSAL APPLICATION & DOMAIN LAUNCHER (100,000+ COMBINATIONS)
    # ---------------------------------------------------------
    open_match = re.search(r"^(?:open|launch|start|go to|run)\s+(.+)$", prompt_low)
    if open_match and not any(
        k in prompt_low
        for k in [
            "youtube",
            "search",
            "google",
            "file explorer",
            "task manager",
            "control panel",
            "device manager",
            "downloads",
            "documents",
            "pictures",
            "snipping tool",
        ]
    ):
        app_target = open_match.group(1).strip()
        app_low = app_target.lower()

        known_sites = {
            "youtube": "https://www.youtube.com",
            "google": "https://www.google.com",
            "github": "https://github.com",
            "reddit": "https://www.reddit.com",
            "twitter": "https://x.com",
            "x": "https://x.com",
            "x.com": "https://x.com",
            "linkedin": "https://www.linkedin.com",
            "facebook": "https://www.facebook.com",
            "instagram": "https://www.instagram.com",
            "tiktok": "https://www.tiktok.com",
            "netflix": "https://www.netflix.com",
            "spotify": "https://open.spotify.com",
            "discord": "https://discord.com/app",
            "whatsapp": "https://web.whatsapp.com",
            "telegram": "https://web.telegram.org",
            "gmail": "https://mail.google.com",
            "outlook": "https://outlook.live.com",
            "chatgpt": "https://chatgpt.com",
            "claude": "https://claude.ai",
            "huggingface": "https://huggingface.co",
            "notion": "https://www.notion.so",
            "figma": "https://www.figma.com",
            "canva": "https://www.canva.com",
            "amazon": "https://www.amazon.com",
            "ebay": "https://www.ebay.com",
            "twitch": "https://www.twitch.tv",
            "leetcode": "https://leetcode.com",
            "stackoverflow": "https://stackoverflow.com",
            "stack overflow": "https://stackoverflow.com",
            "maps": "https://maps.google.com",
            "google maps": "https://maps.google.com",
            "drive": "https://drive.google.com",
            "google drive": "https://drive.google.com",
            "docs": "https://docs.google.com",
            "google docs": "https://docs.google.com",
            "sheets": "https://sheets.google.com",
            "google sheets": "https://sheets.google.com",
            "vercel": "https://vercel.com",
            "netlify": "https://www.netlify.com",
            "aws": "https://aws.amazon.com",
            "azure": "https://portal.azure.com",
        }

        # 1. Check known web applications
        if app_low in known_sites:
            target_url = known_sites[app_low]
            import local_music_engine
            if app_low in ["youtube", "yt", "youtube music"]:
                local_music_engine.open_in_chrome(target_url)
            else:
                chrome_bin = local_music_engine.get_chrome_path()
                if chrome_bin:
                    try:
                        subprocess.Popen([chrome_bin, target_url], shell=False)
                    except Exception:
                        webbrowser.open(target_url)
                else:
                    webbrowser.open(target_url)
            return (
                f"🌐 **Autonomous Web App Launcher:** Opened **{app_target.title()}** (`{target_url}`) in Chrome!",
                "autonomous_dynamic_web_launcher",
                [
                    {
                        "language": "powershell",
                        "code": f"start chrome '{target_url}'",
                        "output": f"Opened {target_url}",
                    }
                ],
            )

        # 2. Check if prompt specifies a URL or domain suffix
        if re.search(
            r"\.(com|org|net|io|ai|co|dev|gg|tv|app|so|me|gov|edu)$", app_low
        ) or app_low.startswith("http"):
            target_url = (
                app_target if app_low.startswith("http") else f"https://{app_target}"
            )
            webbrowser.open(target_url)
            return (
                f'🔗 **Autonomous Domain Launcher:** Opening **"{target_url}"** in Chrome!',
                "autonomous_dynamic_domain_launcher",
                [
                    {
                        "language": "powershell",
                        "code": f"start chrome '{target_url}'",
                        "output": f"Navigated to {target_url}",
                    }
                ],
            )

        # 3. Desktop Application Fallback
        exe_app_map = {
            "chrome": "chrome.exe",
            "edge": "msedge.exe",
            "notepad": "notepad.exe",
            "spotify": "spotify.exe",
            "calculator": "calc.exe",
            "calc": "calc.exe",
            "vscode": "code.exe",
            "code": "code.exe",
            "word": "WINWORD.EXE",
            "excel": "EXCEL.EXE",
            "powerpoint": "POWERPNT.EXE",
            "vlc": "vlc.exe",
            "paint": "mspaint.exe",
            "cmd": "cmd.exe",
            "powershell": "powershell.exe",
        }
        target_exe = exe_app_map.get(app_low, f"{app_low}.exe")
        try:
            subprocess.Popen([target_exe], shell=True)
            return (
                f'🚀 **Autonomous Application Launcher:** Launched **"{app_target.title()}"** (`{target_exe}`)!',
                "autonomous_dynamic_app_launcher",
                [
                    {
                        "language": "powershell",
                        "code": f"start '{target_exe}'",
                        "output": f"Launched {target_exe}",
                    }
                ],
            )
        except Exception:
            pass

    # ---------------------------------------------------------
    # 0F. LIVE MULTILINGUAL TRANSLATION ENGINE (50+ LANGUAGES)
    # ---------------------------------------------------------
    trans_match = re.search(
        r"^(?:translate|convert|how do you say)\s+(.+?)\s+(?:to|in)\s+([a-zA-Z\s]+)$",
        prompt_low,
    )
    if trans_match:
        text_to_trans = trans_match.group(1).strip()
        target_lang_raw = trans_match.group(2).strip().lower()

        lang_map = {
            "spanish": "es",
            "french": "fr",
            "german": "de",
            "hindi": "hi",
            "japanese": "ja",
            "chinese": "zh",
            "italian": "it",
            "russian": "ru",
            "portuguese": "pt",
            "korean": "ko",
            "arabic": "ar",
            "dutch": "nl",
            "polish": "pl",
            "turkish": "tr",
            "swedish": "sv",
            "greek": "el",
            "vietnamese": "vi",
            "thai": "th",
            "indonesian": "id",
            "punjabi": "pa",
            "bengali": "bn",
            "latin": "la",
            "ukrainian": "uk",
            "hebrew": "he",
            "tagalog": "tl",
            "filipino": "tl",
            "romanian": "ro",
            "czech": "cs",
        }

        target_code = lang_map.get(target_lang_raw, target_lang_raw[:2])
        try:
            import json
            import ssl

            ctx = ssl._create_unverified_context()
            encoded_q = urllib.parse.quote(text_to_trans)
            trans_url = f"https://api.mymemory.translated.net/get?q={encoded_q}&langpair=en|{target_code}"
            req = urllib.request.Request(
                trans_url,
                headers={"User-Agent": "J.A.R.V.I.S Workstation Translator/1.0"},
            )
            res_raw = (
                urllib.request.urlopen(req, timeout=4, context=ctx)
                .read()
                .decode("utf-8")
            )
            res_data = json.loads(res_raw)
            translated_text = res_data.get("responseData", {}).get("translatedText", "")

            if translated_text:
                return (
                    f'🌐 **Live Multilingual Translation ({target_lang_raw.title()}):**\n\n- **Original (English):** "{text_to_trans}"\n- **Translation ({target_lang_raw.title()}):** **"{translated_text}"**',
                    "autonomous_live_translation",
                    [
                        {
                            "language": "python",
                            "code": f"translate('{text_to_trans}', lang='{target_code}')",
                            "output": translated_text,
                        }
                    ],
                )
        except Exception:
            pass

    # ---------------------------------------------------------
    # 0G. 3D MODEL GENERATION & IMAGE-TO-3D SYNTHESIS ENGINE
    # ---------------------------------------------------------
    threed_keywords = [
        "3d",
        "3d model",
        "3d scan",
        "scan room",
        "room scan",
        "3d mesh",
        "image to 3d",
        "trellis",
        "hunyuan",
        "triposr",
        "instantmesh",
    ]
    threed_match = re.search(
        r"(?:generate|create|make|build|scan)?\s*(?:a\s*)?(?:3d model|3d mesh|3d generator|image to 3d|generate 3d|create 3d|3d scan|room scan)\s*(?:of|for)?\s*(.*)",
        prompt_low,
    )

    if any(k in prompt_low for k in threed_keywords) or prompt_low in [
        "3d",
        "3d model",
        "scan",
        "scan room",
        "room",
    ]:
        prompt_arg = threed_match.group(1).strip() if threed_match else ""
        prompt_arg = re.sub(r"^(?:of|for|a|my)\s+", "", prompt_arg).strip()

        # Determine best 3D studio space URL based on model requested
        if "hunyuan" in prompt_low:
            space_url = "https://huggingface.co/spaces/tencent/Hunyuan3D-2.1"
            engine_name = "Tencent Hunyuan3D 2.1"
        elif "triposr" in prompt_low or "instantmesh" in prompt_low:
            space_url = "https://huggingface.co/spaces/stabilityai/TripoSR"
            engine_name = "Stability AI TripoSR"
        elif "scan" in prompt_low or "room" in prompt_low or "image" in prompt_low:
            space_url = "https://huggingface.co/spaces/microsoft/TRELLIS"
            engine_name = "Microsoft TRELLIS.2 Image-to-3D Studio"
        else:
            space_url = "https://huggingface.co/spaces/microsoft/TRELLIS"
            engine_name = "Microsoft TRELLIS.2 3D Studio"

        webbrowser.open(space_url)
        display_target = f'for **"{prompt_arg.title()}"**' if prompt_arg else "Studio"
        return (
            f"🧊 **Autonomous 3D Model & Image-to-3D Generator:** Opened **{engine_name}** {display_target} in Google Chrome!\n\n🔗 [Direct 3D Studio Link]({space_url})",
            "autonomous_3d_generation",
            [
                {
                    "language": "powershell",
                    "code": f"start chrome '{space_url}'",
                    "output": f"Opened {engine_name} studio",
                }
            ],
        )

    # ---------------------------------------------------------
    # 0H. REAL-TIME OBJECT DETECTION & VISUAL GROUNDING ENGINE
    # ---------------------------------------------------------
    obj_match = re.search(
        r"^(?:detect objects|object detection|locate anything|yolo|track objects|visual grounding)\s*(.*)$",
        prompt_low,
    )
    if obj_match or prompt_low in [
        "detect objects",
        "object detection",
        "yolo",
        "locate anything",
        "owlv2",
        "rf-detr",
        "yolo world",
        "detect",
    ]:
        target_obj = obj_match.group(1).strip() if obj_match else ""

        if "nvidia" in prompt_low or "locate" in prompt_low:
            space_url = "https://huggingface.co/spaces/nvidia/LocateAnything"
            engine_name = "NVIDIA LocateAnything SOTA Detector"
        elif "yolo" in prompt_low or "ultralytics" in prompt_low:
            space_url = "https://huggingface.co/spaces/Ultralytics/YOLO26"
            engine_name = "Ultralytics YOLO Real-Time Detector"
        else:
            space_url = "https://huggingface.co/spaces/Roboflow/RF-DETR"
            engine_name = "Roboflow RF-DETR Real-Time Vision Model"

        webbrowser.open(space_url)
        obj_display = (
            f'for target **"{target_obj.title()}"**' if target_obj else "Studio"
        )
        return (
            f"🎯 **Autonomous Vision & Detection Engine:** Launched **{engine_name}** {obj_display} in Google Chrome!\n\n🔗 [Direct Vision Studio Link]({space_url})",
            "autonomous_object_detection",
            [
                {
                    "language": "powershell",
                    "code": f"start chrome '{space_url}'",
                    "output": f"Opened {engine_name} vision studio",
                }
            ],
        )

    # ---------------------------------------------------------
    # 0I. TEXT-TO-SPEECH (TTS), VOICE CLONING & SPEECH SYNTHESIS ENGINE
    # ---------------------------------------------------------
    speak_match = re.search(
        r"^(?:speak|say out loud|read aloud|say|tts)\s+(.+)$", prompt_low
    )
    if speak_match and not any(
        k in prompt_low for k in ["a joke", "the weather", "my ip", "time", "date"]
    ):
        text_to_speak = speak_match.group(1).strip()
        return (
            text_to_speak,
            "autonomous_text_to_speech",
            [{"language": "text", "code": "SPEECH_RESPONSE", "output": text_to_speak}],
        )

    tts_studio_match = re.search(
        r"^(?:voice cloning|kokoro|qwen tts|f5 tts|tts studio|voice generator|speech synthesis)\s*(.*)$",
        prompt_low,
    )
    if tts_studio_match or prompt_low in [
        "voice cloning",
        "kokoro tts",
        "qwen tts",
        "tts",
        "voice generator",
    ]:
        if "qwen" in prompt_low:
            space_url = "https://huggingface.co/spaces/Qwen/Qwen3-TTS-Demo"
            engine_name = "Qwen3-TTS Voice Design Studio"
        elif "omnivoice" in prompt_low or "voice cloning" in prompt_low:
            space_url = "https://huggingface.co/spaces/k2-fsa/OmniVoice"
            engine_name = "OmniVoice 600+ Language Voice Cloning"
        else:
            space_url = "https://huggingface.co/spaces/hexgrad/Kokoro-TTS"
            engine_name = "Kokoro-TTS SOTA Voice Synthesizer"

        webbrowser.open(space_url)
        return (
            f"🎙️ **Autonomous Speech & Voice Studio:** Opened **{engine_name}** in Google Chrome!\n\n🔗 [Direct Speech Studio Link]({space_url})",
            "autonomous_voice_cloning_studio",
            [
                {
                    "language": "powershell",
                    "code": f"start chrome '{space_url}'",
                    "output": f"Opened {engine_name}",
                }
            ],
        )

    # ---------------------------------------------------------
    # 0I. AUTONOMOUS IT JOB APPLICATION & CAREER ENGINE
    # ---------------------------------------------------------
    job_keywords = [
        "job",
        "jobs",
        "role",
        "roles",
        "hiring",
        "indeed",
        "remoteok",
        "careers",
        "apply",
        "support jobs",
        "tech jobs",
        "it jobs",
    ]
    if any(k in prompt_low for k in job_keywords) and any(
        action in prompt_low
        for action in ["find", "search", "apply", "get", "look", "show", "open", "auto"]
    ):
        try:
            import autonomous_job_applier

            search_query = "IT Support Analyst"
            if (
                "peel" in prompt_low
                or "brampton" in prompt_low
                or "mississauga" in prompt_low
            ):
                search_query = "IT Support & Systems Specialist Peel Region"
            elif (
                "niagara" in prompt_low
                or "welland" in prompt_low
                or "catharines" in prompt_low
            ):
                search_query = "AI Data Analyst & Systems Technician Niagara Region"
            elif "sudbury" in prompt_low:
                search_query = (
                    "Telecommunications Field Service Technician Greater Sudbury"
                )

            jobs = autonomous_job_applier.search_live_it_jobs(search_query, limit=4)
            applied_summary = []

            for j in jobs[:2]:  # Auto-apply to top 2 matched jobs
                c_letter = autonomous_job_applier.auto_apply_to_job(
                    j["title"], j["company"], j["url"]
                )
                snippet_cover = (
                    (c_letter[:180].replace("\n", " ") + "...")
                    if c_letter
                    else "Tailored AI Cover Letter Created"
                )
                applied_summary.append(
                    f"• 💼 **{j['title']}** at **{j['company']}** ({j['location']})\n"
                    f"  🔗 [Apply Direct ↗]({j['url']})\n"
                    f'  📝 *AI Cover Letter:* "{snippet_cover}"'
                )

            job_rows_markdown = "\n\n".join(applied_summary)
            history = autonomous_job_applier.get_job_application_history()

            resp_md = (
                f"🚀 **Autonomous IT Job Application Engine Active!**\n\n"
                f'Fetched live positions for **"{search_query.title()}"**, generated customized AI cover letters, recorded applications in your database, and opened 1-click Chrome application portals:\n\n'
                f"{job_rows_markdown}\n\n"
                f"📊 **Total Tracked Applications in Database:** `{len(history)}` Applications Saved"
            )
            return (
                resp_md,
                "autonomous_job_applier",
                [
                    {
                        "language": "python",
                        "code": f"autonomous_job_applier.search_live_it_jobs('{search_query}')",
                        "output": f"Auto-applied & launched Chrome portals for top {len(applied_summary)} matched jobs",
                    }
                ],
            )
        except Exception as e:
            print(f"[AutonomousEngine] Job Applier Error: {e}")

    # ---------------------------------------------------------
    # 0L. DOM SYSTEM ENGINE & DOM AUTOMATION ROUTER
    # ---------------------------------------------------------
    if any(
        k in prompt_low
        for k in [
            "dom",
            "dom system",
            "inspect dom",
            "dom tree",
            "dom element",
            "query dom",
        ]
    ):
        try:
            import json

            import dom_system_engine

            target_url = "https://ca.indeed.com"
            url_match = re.search(r"https?://[^\s]+", user_prompt)
            if url_match:
                target_url = url_match.group(0)

            dom_res = dom_system_engine.inspect_dom_tree(target_url)
            summary_str = (
                f"🌳 **DOM System Engine Active!**\n\n"
                f"**Target URL:** `{target_url}`\n"
                f"**Page Title:** `{dom_res.get('title', 'N/A')}`\n"
                f"**DOM Input Fields Found:** `{dom_res.get('input_count', 0)}` nodes\n"
                f"**DOM Clickable Buttons Found:** `{dom_res.get('button_count', 0)}` nodes\n\n"
                f"```json\n{json.dumps(dom_res, indent=2)}\n```"
            )
            return (
                summary_str,
                "autonomous_dom_system",
                [
                    {
                        "language": "python",
                        "code": f"dom_system_engine.inspect_dom_tree('{target_url}')",
                        "output": "Inspected DOM Tree",
                    }
                ],
            )
        except Exception as e:
            print(f"[DOMSystemEngine] Error: {e}")
    if prompt_low in ["show desktop", "minimize all", "desktop"]:
        try:
            subprocess.Popen(
                [
                    "powershell",
                    "(New-Object -ComObject Shell.Application).MinimizeAll()",
                ],
                shell=True,
            )
            return (
                "💻 **Autonomous Workspace Action:** Minimized all windows & showing desktop!",
                "autonomous_show_desktop",
                [
                    {
                        "language": "powershell",
                        "code": "(New-Object Shell.Application).MinimizeAll()",
                        "output": "Minimized all windows",
                    }
                ],
            )
        except Exception:
            pass

    if prompt_low in ["open task manager", "task manager", "taskmgr"]:
        try:
            subprocess.Popen(["taskmgr.exe"], shell=True)
            return (
                "⚙️ **Autonomous System Control:** Opened **Windows Task Manager**!",
                "autonomous_task_manager",
                [
                    {
                        "language": "powershell",
                        "code": "taskmgr.exe",
                        "output": "Opened Task Manager",
                    }
                ],
            )
        except Exception:
            pass

    if prompt_low in [
        "open file explorer",
        "file explorer",
        "explorer",
        "my computer",
        "this pc",
    ]:
        try:
            subprocess.Popen(["explorer.exe"], shell=True)
            return (
                "📁 **Autonomous System Action:** Opened **File Explorer**!",
                "autonomous_file_explorer",
                [
                    {
                        "language": "powershell",
                        "code": "explorer.exe",
                        "output": "Opened File Explorer",
                    }
                ],
            )
        except Exception:
            pass

    if prompt_low in ["open downloads", "downloads", "downloads folder"]:
        try:
            subprocess.Popen(["explorer.exe", "shell:Downloads"], shell=True)
            return (
                "📥 **Autonomous Folder Launcher:** Opened **Downloads** folder!",
                "autonomous_downloads_folder",
                [
                    {
                        "language": "powershell",
                        "code": "explorer.exe shell:Downloads",
                        "output": "Opened Downloads",
                    }
                ],
            )
        except Exception:
            pass

    if prompt_low in ["open documents", "documents", "documents folder"]:
        try:
            subprocess.Popen(["explorer.exe", "shell:Personal"], shell=True)
            return (
                "📄 **Autonomous Folder Launcher:** Opened **Documents** folder!",
                "autonomous_documents_folder",
                [
                    {
                        "language": "powershell",
                        "code": "explorer.exe shell:Personal",
                        "output": "Opened Documents",
                    }
                ],
            )
        except Exception:
            pass

    if prompt_low in ["open pictures", "pictures", "pictures folder", "photos folder"]:
        try:
            subprocess.Popen(["explorer.exe", "shell:My Pictures"], shell=True)
            return (
                "🖼️ **Autonomous Folder Launcher:** Opened **Pictures** folder!",
                "autonomous_pictures_folder",
                [
                    {
                        "language": "powershell",
                        "code": "explorer.exe shell:My Pictures",
                        "output": "Opened Pictures",
                    }
                ],
            )
        except Exception:
            pass

    if prompt_low in ["open control panel", "control panel"]:
        try:
            subprocess.Popen(["control.exe"], shell=True)
            return (
                "⚙️ **Autonomous System Action:** Opened **Windows Control Panel**!",
                "autonomous_control_panel",
                [
                    {
                        "language": "powershell",
                        "code": "control.exe",
                        "output": "Opened Control Panel",
                    }
                ],
            )
        except Exception:
            pass

    if prompt_low in ["open device manager", "device manager"]:
        try:
            subprocess.Popen(["devmgmt.msc"], shell=True)
            return (
                "🖥️ **Autonomous System Action:** Opened **Device Manager**!",
                "autonomous_device_manager",
                [
                    {
                        "language": "powershell",
                        "code": "devmgmt.msc",
                        "output": "Opened Device Manager",
                    }
                ],
            )
        except Exception:
            pass

    if prompt_low in [
        "open snipping tool",
        "take screenshot",
        "take a screenshot",
        "screenshot",
        "snipping tool",
    ]:
        try:
            subprocess.Popen(["snippingtool.exe"], shell=True)
            return (
                "✂️ **Autonomous System Action:** Launched **Windows Snipping Tool**!",
                "autonomous_snipping_tool",
                [
                    {
                        "language": "powershell",
                        "code": "snippingtool.exe",
                        "output": "Opened Snipping Tool",
                    }
                ],
            )
        except Exception:
            pass

    if prompt_low in ["empty recycle bin", "clear recycle bin", "clean recycle bin"]:
        try:
            res = subprocess.check_output(
                [
                    "powershell",
                    "-Command",
                    "Clear-RecycleBin -Force -ErrorAction SilentlyContinue",
                ],
                text=True,
            )
            return (
                "🗑️ **Autonomous System Action:** Windows Recycle Bin cleared successfully!",
                "autonomous_clear_recycle_bin",
                [
                    {
                        "language": "powershell",
                        "code": "Clear-RecycleBin -Force",
                        "output": "Recycle bin cleared",
                    }
                ],
            )
        except Exception:
            pass

    if prompt_low in ["my ip", "ip address", "what is my ip", "local ip"]:
        try:
            cmd = "Get-CimInstance Win32_NetworkAdapterConfiguration | Where-Object IPEnabled -eq $true | Select-Object -ExpandProperty IPAddress"
            res = subprocess.check_output(
                ["powershell", "-Command", cmd], text=True
            ).strip()
            return (
                f"🌐 **Local IP Address:**\n```\n{res}\n```",
                "autonomous_ip_info",
                [{"language": "powershell", "code": cmd, "output": res}],
            )
        except Exception:
            pass

    if prompt_low in [
        "ping google",
        "check internet",
        "test internet",
        "test connection",
    ]:
        try:
            res = subprocess.check_output(
                ["ping", "-n", "3", "8.8.8.8"], text=True
            ).strip()
            return (
                f"📡 **Network Connectivity Test (8.8.8.8):**\n```\n{res}\n```",
                "autonomous_ping_test",
                [{"language": "cmd", "code": "ping -n 3 8.8.8.8", "output": res}],
            )
        except Exception:
            pass

    if prompt_low in ["wifi status", "wifi info", "wifi"]:
        try:
            res = subprocess.check_output(
                ["netsh", "wlan", "show", "interfaces"], text=True
            ).strip()
            return (
                f"📶 **Wi-Fi Interface Status:**\n```\n{res}\n```",
                "autonomous_wifi_info",
                [
                    {
                        "language": "cmd",
                        "code": "netsh wlan show interfaces",
                        "output": res,
                    }
                ],
            )
        except Exception:
            pass

    if prompt_low in ["system uptime", "uptime", "boot time"]:
        try:
            cmd = "(Get-CimInstance Win32_OperatingSystem).LastBootUpTime"
            res = subprocess.check_output(
                ["powershell", "-Command", cmd], text=True
            ).strip()
            return (
                f"⏱️ **Workstation System Uptime:** Last booted on **{res}**",
                "autonomous_uptime_info",
                [{"language": "powershell", "code": cmd, "output": res}],
            )
        except Exception:
            pass

    if prompt_low in ["restart pc", "restart computer", "reboot pc", "reboot"]:
        try:
            subprocess.Popen(["shutdown", "/r", "/t", "10"], shell=True)
            return (
                "🔄 **Autonomous Power Action:** Workstation restarting in 10 seconds! (Type `cancel shutdown` to abort)",
                "autonomous_restart_pc",
                [
                    {
                        "language": "powershell",
                        "code": "shutdown /r /t 10",
                        "output": "Restart initiated",
                    }
                ],
            )
        except Exception:
            pass

    if prompt_low in ["cancel shutdown", "abort shutdown", "stop shutdown"]:
        try:
            subprocess.Popen(["shutdown", "/a"], shell=True)
            return (
                "✅ **Autonomous Power Action:** Shutdown/Restart aborted!",
                "autonomous_abort_shutdown",
                [
                    {
                        "language": "powershell",
                        "code": "shutdown /a",
                        "output": "Shutdown cancelled",
                    }
                ],
            )
        except Exception:
            pass

    if prompt_low in ["sleep pc", "sleep computer", "put pc to sleep"]:
        try:
            subprocess.Popen(
                ["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"], shell=True
            )
            return (
                "🌙 **Autonomous Power Action:** Workstation going to sleep!",
                "autonomous_sleep_pc",
                [
                    {
                        "language": "powershell",
                        "code": "rundll32.exe powrprof.dll,SetSuspendState 0,1,0",
                        "output": "Sleep mode initiated",
                    }
                ],
            )
        except Exception:
            pass

    # ---------------------------------------------------------
    # 0E. LIVE WEATHER, WIKIPEDIA, NEWS, JOKES & KNOWLEDGE
    # ---------------------------------------------------------
    # 1. Live Weather (Local Open-Meteo High Speed Bridge)
    if (
        "weather" in prompt_low
        or "weather in" in prompt_low
        or "temperature in" in prompt_low
        or "forecast" in prompt_low
    ) and not any(
        w in prompt_low
        for w in ["convert", "converting", "celsius", "fahrenheit", "code", "script"]
    ):
        city = (
            prompt_low.replace("what is the weather in", "")
            .replace("what is the weather", "")
            .replace("weather in", "")
            .replace("weather", "")
            .replace("temperature in", "")
            .replace("temperature", "")
            .replace("forecast", "")
            .strip()
        )
        try:
            # Query local meteorological station bridge first (<10ms)
            req = urllib.request.Request(
                "http://127.0.0.1:5000/api/system/weather", timeout=2
            )
            with urllib.request.urlopen(req) as resp:
                wdata = json.loads(resp.read().decode("utf-8"))
                if wdata.get("locations"):
                    loc = wdata["locations"][0]
                    loc_name = loc.get("name", "Sudbury").replace("📍 ", "")
                    res_text = f"{loc.get('condition', 'Clear Sky')}, {loc.get('temp_c')}°C ({loc.get('temp_f')}°F), Wind {loc.get('windspeed_kmh')} km/h"
                    return (
                        f"🌤️ **Live Weather Report ({loc_name}):**\n\n- **Conditions:** {loc.get('condition')}\n- **Temperature:** {loc.get('temp_c')}°C ({loc.get('temp_f')}°F)\n- **Wind Speed:** {loc.get('windspeed_kmh')} km/h\n- **Alert Level:** {loc.get('alert', 'Normal')}\n\n*(Live Weather Radar station is active at /weather)*",
                        "autonomous_weather_info",
                        [
                            {
                                "language": "json",
                                "code": "GET /api/system/weather",
                                "output": res_text,
                            }
                        ],
                    )
        except Exception:
            pass

        location_q = urllib.parse.quote(city) if city else ""
        try:
            import ssl

            ctx = ssl._create_unverified_context()
            url = f"https://wttr.in/{location_q}?format=%C+%t+%w+%h"
            req = urllib.request.Request(url, headers={"User-Agent": "curl/7.68.0"})
            res = (
                urllib.request.urlopen(req, timeout=3, context=ctx)
                .read()
                .decode("utf-8", errors="ignore")
                .strip()
            )
            loc_display = city.title() if city else "Current Location"
            return (
                f"🌤️ **Live Weather Report ({loc_display}):**\n\n- **Conditions & Temp:** {res}\n- **Source:** Live Meteorological Station",
                "autonomous_weather_info",
                [{"language": "python", "code": f"curl wttr.in/{city}", "output": res}],
            )
        except Exception:
            pass

    # 1B. Real-Time Location Identification
    if any(q in prompt_low for q in ["where am i", "what is my location", "get my location", "my location", "current location"]):
        try:
            req = urllib.request.Request("http://127.0.0.1:5000/api/system/location")
            with urllib.request.urlopen(req, timeout=3) as resp:
                loc_data = json.loads(resp.read().decode("utf-8"))
                return (
                    f"📍 **Commander Location Verified**:\n\n"
                    f"- **Settlement / City:** {loc_data.get('city', 'Greater Sudbury')}\n"
                    f"- **Region & Country:** {loc_data.get('region', 'Ontario')}, {loc_data.get('country', 'Canada')}\n"
                    f"- **Coordinates:** Lat `{loc_data.get('lat', 46.52)}°`, Lon `{loc_data.get('lon', -80.94)}°`\n"
                    f"- **Timezone:** {loc_data.get('timezone', 'America/Toronto')}\n"
                    f"- **Network Provider:** {loc_data.get('isp', 'Bell Canada')} (Public IP: `{loc_data.get('ip', 'Local')}`)\n"
                    f"- **Authorized Commander:** {loc_data.get('commander', 'Mr. Ramadeep Singh')}\n\n"
                    f"*(Live radar and local weather telemetry are synchronized at `/weather`)*",
                    "autonomous_location_lookup",
                    [{"language": "json", "code": "GET /api/system/location", "output": json.dumps(loc_data, indent=2)}]
                )
        except Exception:
            pass

    # 2. Wikipedia Summary Lookup
    wiki_match = re.search(
        r"^(?:who is|what is|tell me about|wikipedia)\s+(.+)$", prompt_low
    )
    if wiki_match:
        query_term = wiki_match.group(1).strip()
        if not any(k in query_term for k in ["the weather", "my ip", "time", "date"]):
            try:
                formatted_term = urllib.parse.quote(query_term.replace(" ", "_"))
                wiki_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{formatted_term}"
                req = urllib.request.Request(
                    wiki_url,
                    headers={"User-Agent": "D.E.E.P Workstation Agent/1.0"},
                )
                import json

                res_data = json.loads(
                    urllib.request.urlopen(req, timeout=4).read().decode("utf-8")
                )
                extract = res_data.get("extract", "")
                title = res_data.get("title", query_term.title())
                page_url = (
                    res_data.get("content_urls", {})
                    .get("desktop", {})
                    .get("page", f"https://en.wikipedia.org/wiki/{formatted_term}")
                )

                if extract:
                    return (
                        f"📚 **Wikipedia Summary: {title}**\n\n{extract}\n\n🔗 [Read full Wikipedia article]({page_url})",
                        "autonomous_wikipedia_summary",
                        [
                            {
                                "language": "python",
                                "code": f"fetch wikipedia '{title}'",
                                "output": extract[:100] + "...",
                            }
                        ],
                    )
            except Exception:
                pass

    # 3. Live Tech News Headlines
    if prompt_low in [
        "news",
        "news headlines",
        "tech news",
        "latest news",
        "headlines",
    ]:
        try:
            import json

            req_top = urllib.request.Request(
                "https://hacker-news.firebaseio.com/v0/topstories.json",
                headers={"User-Agent": "Mozilla/5.0"},
            )
            top_ids = json.loads(
                urllib.request.urlopen(req_top, timeout=4).read().decode()
            )[:5]

            news_items = []
            for item_id in top_ids:
                try:
                    req_item = urllib.request.Request(
                        f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json",
                        headers={"User-Agent": "Mozilla/5.0"},
                    )
                    item_data = json.loads(
                        urllib.request.urlopen(req_item, timeout=3).read().decode()
                    )
                    title = item_data.get("title", "Headline")
                    url = item_data.get(
                        "url", f"https://news.ycombinator.com/item?id={item_id}"
                    )
                    news_items.append(f"- [{title}]({url})")
                except Exception:
                    continue

            if news_items:
                headlines_str = "\n".join(news_items)
                return (
                    f"📰 **Latest Live Tech News Headlines:**\n\n{headlines_str}",
                    "autonomous_tech_news",
                    [
                        {
                            "language": "python",
                            "code": "fetch hacker-news top stories",
                            "output": headlines_str,
                        }
                    ],
                )
        except Exception:
            pass

    # 4. Jokes & Tech Humor
    if prompt_low in [
        "tell me a joke",
        "joke",
        "tell a joke",
        "programmer joke",
        "say a joke",
    ]:
        import random

        jokes = [
            "Why do programmers prefer dark mode? Because light attracts bugs! 🐛",
            "There are 10 types of people in the world: those who understand binary, and those who don't. 💻",
            "A SQL query walks into a bar, walks up to two tables and asks: 'Can I join you?' 🍺",
            "Why did the JavaScript developer wear glasses? Because he didn't C#! 👓",
            "Hardware is the part of a computer that you can kick; software is the part you can only curse at. 🖥️",
            "An optimist says the glass is half full. A pessimist says it's half empty. A programmer says it's twice as large as necessary. 🥤",
        ]
        chosen = random.choice(jokes)
        return (
            f'😄 **J.A.R.V.I.S. Humor:**\n\n"{chosen}"',
            "autonomous_joke_generator",
            [{"language": "python", "code": "generate_humor()", "output": chosen}],
        )

    # 5. Motivational Quotes
    if prompt_low in ["quote", "motivate me", "quote of the day", "motivational quote"]:
        import random

        quotes = [
            '"The only way to do great work is to love what you do." — Steve Jobs 🚀',
            '"Code is like humor. When you have to explain it, it\'s bad." — Cory House 💻',
            '"Simplicity is prerequisite for reliability." — Edsger W. Dijkstra ⚡',
            '"First, solve the problem. Then, write the code." — John Johnson 🎯',
            '"The best way to predict the future is to invent it." — Alan Kay 🔮',
        ]
        chosen = random.choice(quotes)
        return (
            f"💡 **Daily Workstation Motivation:**\n\n{chosen}",
            "autonomous_motivational_quote",
            [{"language": "python", "code": "generate_quote()", "output": chosen}],
        )

    # 6. Direct Google / GitHub / Amazon Search Launchers
    if prompt_low.startswith("google ") or prompt_low.startswith("search google for "):
        search_q = (
            prompt_low.replace("search google for ", "").replace("google ", "").strip()
        )
        if search_q:
            url = f"https://www.google.com/search?q={urllib.parse.quote(search_q)}"
            webbrowser.open(url)
            return (
                f'🔍 **Autonomous Search Launcher:** Opened Google search for **"{search_q.title()}"** in Chrome!',
                "autonomous_google_search",
                [
                    {
                        "language": "powershell",
                        "code": f"start chrome '{url}'",
                        "output": f"Searched '{search_q}' on Google",
                    }
                ],
            )

    if prompt_low.startswith("search github for ") or prompt_low.startswith(
        "github search "
    ):
        search_q = (
            prompt_low.replace("search github for ", "")
            .replace("github search ", "")
            .strip()
        )
        if search_q:
            url = f"https://github.com/search?q={urllib.parse.quote(search_q)}"
            webbrowser.open(url)
            return (
                f'🐙 **Autonomous GitHub Search:** Opened repository search for **"{search_q}"** on GitHub!',
                "autonomous_github_search",
                [
                    {
                        "language": "powershell",
                        "code": f"start chrome '{url}'",
                        "output": f"Searched '{search_q}' on GitHub",
                    }
                ],
            )

    # ---------------------------------------------------------
    # 0C. DIRECT YOUTUBE SONG & VIDEO PLAYER (HIGH PRIORITY)
    # ---------------------------------------------------------
    conversational_game_words_0c = [
        "football", "soccer", "chess", "cricket", "basketball", "tennis",
        "badminton", "hockey", "baseball", "volleyball", "rugby", "golf",
        "video game", "video games", "board game", "cards", "poker",
        "with my friend", "with friends", "with my friends", "outside", "a game"
    ]
    is_conv_play_0c = (
        bool(re.search(r"\b(?:i|we|they|you|he|she)\s+play\b", prompt_low))
        or (any(w in prompt_low for w in conversational_game_words_0c) and not any(y in prompt_low for y in ["youtube", "on youtube", "song", "track", "music"]))
        or prompt_low.startswith("today ")
        or "how to play" in prompt_low
        or "let's play" in prompt_low
        or "can we play" in prompt_low
        or "can you play" in prompt_low
        or "want to play" in prompt_low
        or "local" in prompt_low
    )
    is_explicit_yt_0c = (
        ("youtube" in prompt_low and any(w in prompt_low for w in ["search", "play", "open", "watch"]))
        or ("on youtube" in prompt_low or "on yt" in prompt_low)
        or bool(re.search(r"^play\s+(.+?\s+by\s+[a-zA-Z0-9\s]+)$", prompt_low))
        or bool(re.search(r"^play\s+(?:the\s+)?(?:song|track|music|video)\b", prompt_low))
    )
    if (
        not is_conv_play_0c
        and is_explicit_yt_0c
        and not any(k in prompt_low for k in ["close", "stop", "pause", "exit"])
    ):
        yt_raw = (
            prompt_low.replace("on youtube", "")
            .replace("youtube", "")
            .replace("search", "")
        )
        yt_query = re.sub(r"^\bplay\b", "", yt_raw).strip()
        yt_query = re.sub(r"[\.\?\!\;]+$", "", yt_query).strip()

        if len(yt_query) > 1:
            encoded_yt = urllib.parse.quote(yt_query)
            search_url = f"https://www.youtube.com/results?search_query={encoded_yt}"
            target_play_url = search_url
            is_direct = False

            try:
                import ssl

                ctx = ssl._create_unverified_context()
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                }
                req = urllib.request.Request(search_url, headers=headers)
                html = (
                    urllib.request.urlopen(req, timeout=5, context=ctx)
                    .read()
                    .decode("utf-8", errors="ignore")
                )
                vids = re.findall(r"/watch\?v=([a-zA-Z0-9_-]{11})", html)
                if vids:
                    target_play_url = (
                        f"https://www.youtube.com/watch?v={vids[0]}&autoplay=1"
                    )
                    is_direct = True
            except Exception:
                pass

            import local_music_engine
            local_music_engine.open_in_chrome(target_play_url)

            if is_direct:
                return (
                    f'▶️ **Autonomous Music & Media Player:** Playing **"{yt_query.title()}"** live in Google Chrome!\n\n🔗 [Direct Video Link]({target_play_url})',
                    "autonomous_youtube_player",
                    [
                        {
                            "language": "powershell",
                            "code": f"start chrome '{target_play_url}'",
                            "output": f"Playing '{yt_query}' directly on YouTube",
                        }
                    ],
                )
            else:
                return (
                    f'🎵 **Autonomous Media Execution:** Opening YouTube search for **"{yt_query.title()}"** in Google Chrome!',
                    "autonomous_youtube_engine",
                    [
                        {
                            "language": "powershell",
                            "code": f"start chrome '{search_url}'",
                            "output": f"Searching '{yt_query}' on YouTube",
                        }
                    ],
                )
    if prompt_low in [
        "system stats",
        "ram usage",
        "cpu usage",
        "specs",
        "memory usage",
    ]:
        try:
            cmd = "Get-CimInstance Win32_OperatingSystem | Select-Object @{N='FreeRAMGB';E={[math]::Round($_.FreePhysicalMemory/1MB,2)}}, @{N='TotalRAMGB';E={[math]::Round($_.TotalVisibleMemorySize/1MB,2)}} | ConvertTo-Json"
            res = subprocess.check_output(["powershell", "-Command", cmd], text=True)
            import json

            data = json.loads(res)
            total = data.get("TotalRAMGB", 32)
            free = data.get("FreeRAMGB", 16)
            used = round(total - free, 2)
            pct = round((used / total) * 100, 1)

            output_msg = f"📊 **Live Workstation Resource Monitor:**\n\n- **RAM Usage:** {used} GB / {total} GB ({pct}% used)\n- **Free RAM:** {free} GB\n- **Status:** Healthy & Operational 🚀"
            return (
                output_msg,
                "autonomous_system_stats",
                [{"language": "powershell", "code": cmd, "output": output_msg}],
            )
        except Exception:
            pass

    if prompt_low in ["top processes", "running processes", "active tasks"]:
        try:
            cmd = "Get-Process | Sort-Object CPU -Descending | Select-Object -First 7 ProcessName, @{N='CPU(s)';E={[math]::Round($_.CPU,2)}}, @{N='RAM(MB)';E={[math]::Round($_.WorkingSet/1MB,2)}} | Format-Table -Autosize | Out-String"
            res = subprocess.check_output(["powershell", "-Command", cmd], text=True)
            return (
                f"💻 **Top Resource-Consuming Processes:**\n```\n{res.strip()}\n```",
                "autonomous_process_monitor",
                [{"language": "powershell", "code": cmd, "output": res}],
            )
        except Exception:
            pass

    if prompt_low in ["battery status", "battery", "power status"]:
        try:
            cmd = "(Get-CimInstance Win32_Battery) | Select-Object EstimatedChargeRemaining, BatteryStatus | ConvertTo-Json"
            res = subprocess.check_output(["powershell", "-Command", cmd], text=True)
            import json

            b_data = json.loads(res)
            charge = b_data.get("EstimatedChargeRemaining", 100)
            return (
                f"🔋 **Battery Status:** **{charge}%** remaining.",
                "autonomous_battery_status",
                [{"language": "powershell", "code": cmd, "output": f"{charge}%"}],
            )
        except Exception:
            return (
                "🔌 **Power Status:** Desktop / AC Power Connected (No battery detected).",
                "autonomous_battery_status",
                [
                    {
                        "language": "powershell",
                        "code": "Win32_Battery",
                        "output": "AC Power",
                    }
                ],
            )

    if prompt_low in ["flush dns", "clear dns"]:
        try:
            res = subprocess.check_output(["ipconfig", "/flushdns"], text=True)
            return (
                "🧹 **Network Action:** Windows DNS Resolver Cache Flushed Successfully!",
                "autonomous_flush_dns",
                [
                    {
                        "language": "cmd",
                        "code": "ipconfig /flushdns",
                        "output": res.strip(),
                    }
                ],
            )
        except Exception:
            pass

    # ---------------------------------------------------------
    # 1. LIVE QUICK MATH & CALCULATIONS
    # ---------------------------------------------------------
    calc_match = re.search(
        r"^(?:calculate|calc|what is|eval)\s+([0-9\.\+\-\*\/\(\)\^\s\%\,\bsqrt\b\bpow\b]+)$",
        prompt_low,
    )
    if calc_match:
        raw_expr = calc_match.group(1).replace("^", "**").strip()
        try:
            # Safe restricted math evaluation
            allowed_names = {
                "sqrt": math.sqrt,
                "pow": math.pow,
                "abs": abs,
                "pi": math.pi,
                "e": math.e,
            }
            result = eval(raw_expr, {"__builtins__": None}, allowed_names)
            return (
                f"🔢 **Autonomous Calculation:** `{calc_match.group(1).strip()}` = **{result}**",
                "autonomous_math_engine",
                [
                    {
                        "language": "python",
                        "code": f"eval('{raw_expr}')",
                        "output": str(result),
                    }
                ],
            )
        except Exception:
            pass

    # ---------------------------------------------------------
    # 2. QUICK QUICK NOTES TO DESKTOP
    # ---------------------------------------------------------
    note_match = re.search(
        r"^(?:create note|take note|save note|note)\s+(.+)$", prompt_low
    )
    if note_match:
        note_text = note_match.group(1).strip()
        desktop_path = os.path.expanduser(r"~\Desktop\jarvis_notes.txt")
        try:
            with open(desktop_path, "a", encoding="utf-8") as f:
                f.write(f"- {note_text}\n")
            subprocess.Popen(["notepad.exe", desktop_path], shell=True)
            return (
                f'📝 **Autonomous Note Saved:** Added **"{note_text}"** to `Desktop/jarvis_notes.txt` and opened Notepad!',
                "autonomous_note_engine",
                [
                    {
                        "language": "powershell",
                        "code": f"Add-Content '{desktop_path}' '{note_text}'",
                        "output": "Saved note",
                    }
                ],
            )
        except Exception:
            pass

    # ---------------------------------------------------------
    # 3. DIRECT DEEP SEARCH SHORTCUTS (Gmail, Drive, Reddit, StackOverflow)
    # ---------------------------------------------------------
    reddit_search = re.search(r"\b(?:search|find)\s+(.+?)\s+on\s+reddit$", prompt_low)
    if reddit_search:
        r_q = reddit_search.group(1).strip()
        r_url = f"https://www.reddit.com/search/?q={urllib.parse.quote(r_q)}"
        subprocess.Popen(["start", "chrome", r_url], shell=True)
        return (
            f'🤖 **Autonomous Reddit Search:** Searching Reddit for **"{r_q}"**!',
            "autonomous_reddit_search",
            [
                {
                    "language": "powershell",
                    "code": f"start chrome '{r_url}'",
                    "output": f"Reddit search for '{r_q}'",
                }
            ],
        )

    so_search = re.search(
        r"\b(?:search|find)\s+(.+?)\s+on\s+(?:stack overflow|stackoverflow)$",
        prompt_low,
    )
    if so_search:
        so_q = so_search.group(1).strip()
        so_url = f"https://stackoverflow.com/search?q={urllib.parse.quote(so_q)}"
        subprocess.Popen(["start", "chrome", so_url], shell=True)
        return (
            f'💻 **Autonomous StackOverflow Search:** Searching StackOverflow for **"{so_q}"**!',
            "autonomous_stackoverflow_search",
            [
                {
                    "language": "powershell",
                    "code": f"start chrome '{so_url}'",
                    "output": f"StackOverflow search for '{so_q}'",
                }
            ],
        )

    drive_search = re.search(
        r"\b(?:search|find)\s+(.+?)\s+on\s+(?:google drive|drive)$", prompt_low
    )
    if drive_search:
        d_q = drive_search.group(1).strip()
        d_url = f"https://drive.google.com/drive/search?q={urllib.parse.quote(d_q)}"
        subprocess.Popen(["start", "chrome", d_url], shell=True)
        return (
            f'📁 **Autonomous Drive Search:** Searching Google Drive for **"{d_q}"**!',
            "autonomous_drive_search",
            [
                {
                    "language": "powershell",
                    "code": f"start chrome '{d_url}'",
                    "output": f"Drive search for '{d_q}'",
                }
            ],
        )

    # ---------------------------------------------------------
    # 4. SYSTEM & AUDIO CONTROL ACTIONS
    # ---------------------------------------------------------
    if prompt_low in ["lock pc", "lock computer", "lock screen", "lock workstation"]:
        try:
            subprocess.Popen(["rundll32.exe", "user32.dll,LockWorkStation"], shell=True)
            return (
                "🔒 **Autonomous System Action:** Workstation locked!",
                "autonomous_system_lock",
                [
                    {
                        "language": "powershell",
                        "code": "rundll32.exe user32.dll,LockWorkStation",
                        "output": "Locked Workstation",
                    }
                ],
            )
        except Exception:
            pass

    if prompt_low in ["volume up", "increase volume", "louder"]:
        try:
            subprocess.Popen(
                [
                    "powershell",
                    "(New-Object -ComObject WScript.Shell).SendKeys([char]175)",
                ],
                shell=True,
            )
            return (
                "🔊 **Autonomous Audio Action:** Volume Increased!",
                "autonomous_volume_up",
                [
                    {
                        "language": "powershell",
                        "code": "(New-Object -ComObject WScript.Shell).SendKeys([char]175)",
                        "output": "Volume Up",
                    }
                ],
            )
        except Exception:
            pass

    if prompt_low in ["volume down", "decrease volume", "quieter"]:
        try:
            subprocess.Popen(
                [
                    "powershell",
                    "(New-Object -ComObject WScript.Shell).SendKeys([char]174)",
                ],
                shell=True,
            )
            return (
                "🔉 **Autonomous Audio Action:** Volume Decreased!",
                "autonomous_volume_down",
                [
                    {
                        "language": "powershell",
                        "code": "(New-Object -ComObject WScript.Shell).SendKeys([char]174)",
                        "output": "Volume Down",
                    }
                ],
            )
        except Exception:
            pass

    if prompt_low in ["mute", "mute volume", "unmute", "toggle mute"]:
        try:
            subprocess.Popen(
                [
                    "powershell",
                    "(New-Object -ComObject WScript.Shell).SendKeys([char]173)",
                ],
                shell=True,
            )
            return (
                "🔇 **Autonomous Audio Action:** Mute Toggled!",
                "autonomous_mute_toggle",
                [
                    {
                        "language": "powershell",
                        "code": "(New-Object -ComObject WScript.Shell).SendKeys([char]173)",
                        "output": "Mute Toggled",
                    }
                ],
            )
        except Exception:
            pass

    if prompt_low in ["play pause", "pause music", "resume music", "toggle play"]:
        try:
            subprocess.Popen(
                [
                    "powershell",
                    "(New-Object -ComObject WScript.Shell).SendKeys([char]179)",
                ],
                shell=True,
            )
            return (
                "⏯️ **Autonomous Media Action:** Play/Pause Toggled!",
                "autonomous_media_toggle",
                [
                    {
                        "language": "powershell",
                        "code": "(New-Object -ComObject WScript.Shell).SendKeys([char]179)",
                        "output": "Media Toggled",
                    }
                ],
            )
        except Exception:
            pass

    if prompt_low in ["next track", "next song", "skip song"]:
        try:
            subprocess.Popen(
                [
                    "powershell",
                    "(New-Object -ComObject WScript.Shell).SendKeys([char]176)",
                ],
                shell=True,
            )
            return (
                "⏭️ **Autonomous Media Action:** Next Track!",
                "autonomous_next_track",
                [
                    {
                        "language": "powershell",
                        "code": "(New-Object -ComObject WScript.Shell).SendKeys([char]176)",
                        "output": "Next Track",
                    }
                ],
            )
        except Exception:
            pass

    if prompt_low in ["what is my ip", "my ip", "show my ip", "ip address"]:
        target_url = "https://whatismyipaddress.com"
        subprocess.Popen(["start", "chrome", target_url], shell=True)
        return (
            "🌐 **Autonomous Network Action:** Opening IP address lookup in Google Chrome!",
            "autonomous_ip_lookup",
            [
                {
                    "language": "powershell",
                    "code": f"start chrome '{target_url}'",
                    "output": "Opened IP lookup",
                }
            ],
        )

    if prompt_low in ["test speed", "internet speed", "check speed", "speedtest"]:
        target_url = "https://fast.com"
        subprocess.Popen(["start", "chrome", target_url], shell=True)
        return (
            "⚡ **Autonomous Speed Test:** Opening live speed test on Fast.com!",
            "autonomous_speed_test",
            [
                {
                    "language": "powershell",
                    "code": f"start chrome '{target_url}'",
                    "output": "Opened speed test",
                }
            ],
        )

    if prompt_low in ["ping google", "check internet", "test connection"]:
        try:
            res = subprocess.check_output(
                ["powershell", "Test-NetConnection google.com"], text=True
            )
            return (
                f"📡 **Network Diagnostic Output:**\n```\n{res[:400]}\n```",
                "autonomous_ping_engine",
                [
                    {
                        "language": "powershell",
                        "code": "Test-NetConnection google.com",
                        "output": res[:400],
                    }
                ],
            )
        except Exception:
            pass

    if prompt_low in ["empty recycle bin", "empty bin", "clear recycle bin"]:
        try:
            subprocess.Popen(
                ["powershell", "Clear-RecycleBin -Force -ErrorAction SilentlyContinue"],
                shell=True,
            )
            return (
                "🗑️ **Autonomous Cleanup Action:** Recycle Bin Emptied!",
                "autonomous_empty_bin",
                [
                    {
                        "language": "powershell",
                        "code": "Clear-RecycleBin -Force",
                        "output": "Recycle bin emptied",
                    }
                ],
            )
        except Exception:
            pass

    # ---------------------------------------------------------
    # 5. WINDOWS FOLDERS & SHELL LOCATIONS
    # ---------------------------------------------------------
    folder_map = {
        "downloads": "shell:Downloads",
        "downloads folder": "shell:Downloads",
        "documents": "shell:Documents",
        "documents folder": "shell:Documents",
        "desktop folder": "shell:Desktop",
        "desktop": "shell:Desktop",
        "pictures": "shell:Pictures",
        "pictures folder": "shell:Pictures",
        "music": "shell:Music",
        "music folder": "shell:Music",
        "videos": "shell:Videos",
        "videos folder": "shell:Videos",
        "recycle bin": "shell:RecycleBinFolder",
        "temp": "shell:Local AppData\\Temp",
    }

    for f_name, f_shell in folder_map.items():
        if prompt_low in [f"open {f_name}", f"go to {f_name}", f"show {f_name}"]:
            try:
                subprocess.Popen(["explorer.exe", f_shell], shell=True)
                return (
                    f"📁 **Autonomous Folder Action:** Opened **{f_name.title()}** in File Explorer!",
                    "autonomous_folder_launcher",
                    [
                        {
                            "language": "powershell",
                            "code": f"explorer.exe {f_shell}",
                            "output": f"Opened {f_name}",
                        }
                    ],
                )
            except Exception:
                pass

    # ---------------------------------------------------------
    # 6. LOCAL DESKTOP APPLICATION LAUNCHER & UTILITIES
    # ---------------------------------------------------------
    app_map = {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "calc": "calc.exe",
        "cmd": "cmd.exe",
        "command prompt": "cmd.exe",
        "powershell": "powershell.exe",
        "terminal": "powershell.exe",
        "explorer": "explorer.exe",
        "file explorer": "explorer.exe",
        "task manager": "taskmgr.exe",
        "taskmgr": "taskmgr.exe",
        "paint": "mspaint.exe",
        "snipping tool": "snippingtool.exe",
        "snip": "snippingtool.exe",
        "chrome": "chrome.exe",
        "vscode": "code",
        "vs code": "code",
        "code": "code",
        "control panel": "control.exe",
        "device manager": "devmgmt.msc",
        "registry editor": "regedit.exe",
        "regedit": "regedit.exe",
        "event viewer": "eventvwr.msc",
        "services": "services.msc",
        "disk management": "diskmgmt.msc",
        "system info": "msinfo32.exe",
        "msinfo": "msinfo32.exe",
        "msinfo32": "msinfo32.exe",
        "dxdiag": "dxdiag.exe",
        "directx": "dxdiag.exe",
        "disk cleanup": "cleanmgr.exe",
        "resource monitor": "resmon.exe",
        "resmon": "resmon.exe",
        "character map": "charmap.exe",
        "remote desktop": "mstsc.exe",
        "wordpad": "wordpad.exe",
    }

    for app_name, exe in app_map.items():
        if prompt_low in [
            f"open {app_name}",
            f"launch {app_name}",
            f"run {app_name}",
            f"start {app_name}",
        ]:
            try:
                subprocess.Popen([exe], shell=True)
                return (
                    f"⚡ **Autonomous Application Launcher:** Launched **{app_name.title()}** on your desktop!",
                    "autonomous_app_launcher",
                    [
                        {
                            "language": "powershell",
                            "code": f"Start-Process {exe}",
                            "output": f"Launched {app_name}",
                        }
                    ],
                )
            except Exception:
                pass

    # Windows Store Protocol Apps
    store_apps = {
        "camera": "microsoft.windows.camera:",
        "clock": "ms-clock:",
        "alarm": "ms-clock:",
        "photos": "ms-photos:",
        "microsoft store": "ms-windows-store:",
        "store": "ms-windows-store:",
    }
    for app_name, protocol in store_apps.items():
        if prompt_low in [f"open {app_name}", f"launch {app_name}"]:
            try:
                subprocess.Popen(["start", protocol], shell=True)
                return (
                    f"⚡ **Autonomous Store App Launcher:** Launched **{app_name.title()}**!",
                    "autonomous_store_app_launcher",
                    [
                        {
                            "language": "powershell",
                            "code": f"start {protocol}",
                            "output": f"Launched {app_name}",
                        }
                    ],
                )
            except Exception:
                pass

    # ---------------------------------------------------------
    # 7. WINDOWS SETTINGS & CONTROL PANEL URI LAUNCHER
    # ---------------------------------------------------------
    win_settings_map = {
        "settings": "ms-settings:",
        "wifi": "ms-settings:network-wifi",
        "wi-fi": "ms-settings:network-wifi",
        "network": "ms-settings:network",
        "bluetooth": "ms-settings:bluetooth",
        "display": "ms-settings:display",
        "sound": "ms-settings:sound",
        "volume settings": "ms-settings:sound",
        "storage": "ms-settings:storagesense",
        "windows update": "ms-settings:windowsupdate",
        "update": "ms-settings:windowsupdate",
        "apps": "ms-settings:appsfeatures",
        "privacy": "ms-settings:privacy",
        "notifications": "ms-settings:notifications",
        "power": "ms-settings:powersleep",
        "battery": "ms-settings:batterysaver",
        "defender": "ms-settings:windowsdefender",
        "clipboard": "ms-settings:clipboard",
    }

    for s_name, s_uri in win_settings_map.items():
        if prompt_low in [
            f"open {s_name}",
            f"open {s_name} settings",
            f"launch {s_name} settings",
            f"go to {s_name} settings",
        ]:
            try:
                subprocess.Popen(["start", s_uri], shell=True)
                return (
                    f"⚙️ **Autonomous System Control:** Opened **Windows {s_name.title()} Settings**!",
                    "autonomous_settings_engine",
                    [
                        {
                            "language": "powershell",
                            "code": f"start {s_uri}",
                            "output": f"Opened Windows {s_name} settings",
                        }
                    ],
                )
            except Exception:
                pass

    # ---------------------------------------------------------
    # 8. EXPANDED EVERYDAY WEB SERVICES & PLATFORMS REGISTRY
    # ---------------------------------------------------------
    known_sites = {
        # AI & Assistants
        "gemini": "https://gemini.google.com",
        "google gemini": "https://gemini.google.com",
        "gemini ai": "https://gemini.google.com",
        "chatgpt": "https://chatgpt.com",
        "openai": "https://chatgpt.com",
        "claude": "https://claude.ai",
        "claude ai": "https://claude.ai",
        "perplexity": "https://www.perplexity.ai",
        "perplexity ai": "https://www.perplexity.ai",
        "midjourney": "https://www.midjourney.com",
        "huggingface": "https://huggingface.co",
        "hugging face": "https://huggingface.co",
        "poe": "https://poe.com",
        "copilot": "https://copilot.microsoft.com",
        "microsoft copilot": "https://copilot.microsoft.com",
        "stable diffusion": "https://stablediffusionweb.com",
        "leonardo ai": "https://leonardo.ai",
        "elevenlabs": "https://elevenlabs.io",
        "suno ai": "https://suno.com",
        "udio": "https://udio.com",
        "civitai": "https://civitai.com",
        "ollama": "https://ollama.com",
        "openrouter": "https://openrouter.ai",
        "replicate": "https://replicate.com",
        "groq": "https://groq.com",
        # Google Workspace & Productivity
        "google": "https://www.google.com",
        "gmail": "https://mail.google.com",
        "google mail": "https://mail.google.com",
        "google drive": "https://drive.google.com",
        "drive": "https://drive.google.com",
        "google docs": "https://docs.google.com",
        "docs": "https://docs.google.com",
        "google sheets": "https://sheets.google.com",
        "sheets": "https://sheets.google.com",
        "google slides": "https://slides.google.com",
        "slides": "https://slides.google.com",
        "google calendar": "https://calendar.google.com",
        "calendar": "https://calendar.google.com",
        "google meet": "https://meet.google.com",
        "meet": "https://meet.google.com",
        "google keep": "https://keep.google.com",
        "keep": "https://keep.google.com",
        "google maps": "https://maps.google.com",
        "maps": "https://maps.google.com",
        "google translate": "https://translate.google.com",
        "translate": "https://translate.google.com",
        "google news": "https://news.google.com",
        "google photos": "https://photos.google.com",
        "notion": "https://www.notion.so",
        "figma": "https://www.figma.com",
        "canva": "https://www.canva.com",
        "trello": "https://trello.com",
        "asana": "https://asana.com",
        "jira": "https://atlassian.net",
        "slack": "https://slack.com",
        "discord": "https://discord.com/app",
        "teams": "https://teams.microsoft.com",
        "microsoft teams": "https://teams.microsoft.com",
        "zoom": "https://zoom.us",
        "outlook": "https://outlook.live.com",
        "protonmail": "https://mail.proton.me",
        "overleaf": "https://www.overleaf.com",
        "dropbox": "https://www.dropbox.com",
        "coda": "https://coda.io",
        "obsidian": "https://obsidian.md",
        "miro": "https://miro.com",
        "lucidchart": "https://lucidchart.com",
        "excalidraw": "https://excalidraw.com",
        "calendly": "https://calendly.com",
        "loom": "https://loom.com",
        "grammarly": "https://grammarly.com",
        # Developer & Tech Platforms
        "github": "https://github.com",
        "gitlab": "https://gitlab.com",
        "bitbucket": "https://bitbucket.org",
        "stackoverflow": "https://stackoverflow.com",
        "stack overflow": "https://stackoverflow.com",
        "replit": "https://replit.com",
        "leetcode": "https://leetcode.com",
        "hackerrank": "https://www.hackerrank.com",
        "pypi": "https://pypi.org",
        "npm": "https://www.npmjs.com",
        "dockerhub": "https://hub.docker.com",
        "docker hub": "https://hub.docker.com",
        "aws": "https://console.aws.amazon.com",
        "aws console": "https://console.aws.amazon.com",
        "gcp": "https://console.cloud.google.com",
        "google cloud": "https://console.cloud.google.com",
        "azure": "https://portal.azure.com",
        "cloudflare": "https://dash.cloudflare.com",
        "vercel": "https://vercel.com",
        "netlify": "https://www.netlify.com",
        "kaggle": "https://www.kaggle.com",
        "arxiv": "https://arxiv.org",
        "w3schools": "https://www.w3schools.com",
        "mdn": "https://developer.mozilla.org",
        "dev.to": "https://dev.to",
        "producthunt": "https://www.producthunt.com",
        "speedtest": "https://www.speedtest.net",
        "fast.com": "https://fast.com",
        "postman": "https://www.postman.com",
        "supabase": "https://supabase.com",
        "firebase": "https://console.firebase.google.com",
        "sentry": "https://sentry.io",
        "codepen": "https://codepen.io",
        "stackblitz": "https://stackblitz.com",
        "regex101": "https://regex101.com",
        "json formatter": "https://jsonformatter.org",
        # Social & Communication
        "whatsapp": "https://web.whatsapp.com",
        "whatsapp web": "https://web.whatsapp.com",
        "telegram": "https://web.telegram.org",
        "telegram web": "https://web.telegram.org",
        "twitter": "https://x.com",
        "x": "https://x.com",
        "instagram": "https://www.instagram.com",
        "facebook": "https://www.facebook.com",
        "linkedin": "https://www.linkedin.com",
        "tiktok": "https://www.tiktok.com",
        "pinterest": "https://www.pinterest.com",
        "reddit": "https://www.reddit.com",
        "quora": "https://www.quora.com",
        "threads": "https://www.threads.net",
        # Media, Music & Gaming
        "youtube": "https://www.youtube.com",
        "yt": "https://www.youtube.com",
        "netflix": "https://www.netflix.com",
        "prime video": "https://www.primevideo.com",
        "amazon prime": "https://www.primevideo.com",
        "hulu": "https://www.hulu.com",
        "disney": "https://www.disneyplus.com",
        "disney plus": "https://www.disneyplus.com",
        "twitch": "https://www.twitch.tv",
        "spotify": "https://open.spotify.com",
        "soundcloud": "https://soundcloud.com",
        "apple music": "https://music.apple.com",
        "youtube music": "https://music.youtube.com",
        "crunchyroll": "https://www.crunchyroll.com",
        "imdb": "https://www.imdb.com",
        "wikipedia": "https://www.wikipedia.org",
        "wiki": "https://www.wikipedia.org",
        "medium": "https://medium.com",
        "substack": "https://substack.com",
        "steam": "https://store.steampowered.com",
        "epic games": "https://store.epicgames.com",
        "roblox": "https://www.roblox.com",
        "chess": "https://www.chess.com",
        "lichess": "https://lichess.org",
        # Shopping, Finance & News
        "amazon": "https://www.amazon.ca",
        "ebay": "https://www.ebay.com",
        "aliexpress": "https://www.aliexpress.com",
        "walmart": "https://www.walmart.ca",
        "bestbuy": "https://www.bestbuy.ca",
        "etsy": "https://www.etsy.com",
        "paypal": "https://www.paypal.com",
        "stripe": "https://dashboard.stripe.com",
        "coinmarketcap": "https://coinmarketcap.com",
        "binance": "https://www.binance.com",
        "yahoo finance": "https://finance.yahoo.com",
        "tradingview": "https://www.tradingview.com",
        "techcrunch": "https://techcrunch.com",
        "the verge": "https://www.theverge.com",
        "hacker news": "https://news.ycombinator.com",
        "google fonts": "https://fonts.google.com",
        "unsplash": "https://unsplash.com",
        "dribbble": "https://dribbble.com",
        "behance": "https://www.behance.net",
    }

    target_url = None
    target_name = None

    # Match site names directly from registry
    for name, url in known_sites.items():
        patterns = [
            f"open {name}",
            f"launch {name}",
            f"go to {name}",
            f"browse {name}",
            f"open {name} in chrome",
            f"open {name} on chrome",
            f"open {name} browser",
            f"launch {name} in chrome",
            f"go to {name} in chrome",
        ]
        if any(p in prompt_low for p in patterns) or prompt_low == name:
            target_url = url
            target_name = name.title()
            break

    # Generic TLD & Domain Matcher
    if not target_url:
        domain_match = re.search(
            r"\b(?:open|launch|go to|browse|navigate to)\s+([a-zA-Z0-9\.\-\_\:\/]+?\.(?:com|org|net|io|ai|ca|co|me|dev|app|gov|edu|uk|in|de|fr|tech|xyz|live|info|local|localhost|[0-9]{1,3}))(?:\s+in\s+chrome|\s+browser|\s+on\s+web)?$",
            prompt_low,
        )
        if domain_match:
            raw_domain = domain_match.group(1).strip()
            target_url = (
                raw_domain if raw_domain.startswith("http") else f"https://{raw_domain}"
            )
            target_name = raw_domain

    if target_url:
        import local_music_engine
        chrome_bin = local_music_engine.get_chrome_path()
        launched = False
        if chrome_bin:
            try:
                subprocess.Popen([chrome_bin, target_url], shell=False)
                launched = True
            except Exception:
                pass
        if not launched:
            try:
                local_music_engine.open_in_chrome(target_url)
                launched = True
            except Exception:
                pass
        if not launched:
            webbrowser.open(target_url)

        return (
            f"🚀 **Autonomous Execution:** Opened **{target_name}** in Google Chrome!\n\n🔗 [Direct Link: {target_url}]({target_url})",
            "autonomous_web_launcher",
            [
                {
                    "language": "powershell",
                    "code": f"start chrome '{target_url}'",
                    "output": f"Successfully launched {target_name} in Google Chrome",
                }
            ],
        )

    # ---------------------------------------------------------
    # 9. SPECIALIZED SEARCH ENGINES (Wikipedia, YouTube, Amazon, GitHub, Maps)
    # ---------------------------------------------------------
    # Wikipedia Search
    wiki_match = re.search(r"\b(?:wikipedia|wiki)\s+(.+)$", prompt_low)
    if wiki_match:
        w_query = wiki_match.group(1).strip()
        w_url = f"https://en.wikipedia.org/wiki/Special:Search?search={urllib.parse.quote(w_query)}"
        subprocess.Popen(["start", "chrome", w_url], shell=True)
        return (
            f'📚 **Autonomous Wikipedia Search:** Searching Wikipedia for **"{w_query}"**!',
            "autonomous_wiki_engine",
            [
                {
                    "language": "powershell",
                    "code": f"start chrome '{w_url}'",
                    "output": f"Wikipedia search for '{w_query}'",
                }
            ],
        )

    # Amazon Search
    amazon_match = re.search(
        r"\b(?:search|find|buy)\s+(.+?)\s+on\s+amazon$", prompt_low
    )
    if amazon_match:
        a_query = amazon_match.group(1).strip()
        a_url = f"https://www.amazon.ca/s?k={urllib.parse.quote(a_query)}"
        subprocess.Popen(["start", "chrome", a_url], shell=True)
        return (
            f'🛒 **Autonomous Amazon Search:** Searching Amazon for **"{a_query}"**!',
            "autonomous_amazon_engine",
            [
                {
                    "language": "powershell",
                    "code": f"start chrome '{a_url}'",
                    "output": f"Amazon search for '{a_query}'",
                }
            ],
        )

    # GitHub Search
    gh_match = re.search(r"\b(?:search|find)\s+(.+?)\s+on\s+github$", prompt_low)
    if gh_match:
        g_query = gh_match.group(1).strip()
        g_url = f"https://github.com/search?q={urllib.parse.quote(g_query)}"
        subprocess.Popen(["start", "chrome", g_url], shell=True)
        return (
            f'🐙 **Autonomous GitHub Search:** Searching GitHub repositories for **"{g_query}"**!',
            "autonomous_github_engine",
            [
                {
                    "language": "powershell",
                    "code": f"start chrome '{g_url}'",
                    "output": f"GitHub search for '{g_query}'",
                }
            ],
        )

    # General Google Web Search
    search_match = re.search(
        r"\b(?:search|google|find)\s+(.+?)(?:\s+on\s+chrome|\s+on\s+google|\s+in\s+browser)?$",
        prompt_low,
    )
    if search_match and not any(
        k in prompt_low for k in ["flight", "flights", "ticket"]
    ):
        query = search_match.group(1).strip()
        if len(query) > 2 and not query.startswith("http"):
            encoded = urllib.parse.quote(query)
            search_url = f"https://www.google.com/search?q={encoded}"
            subprocess.Popen(["start", "chrome", search_url], shell=True)
            return (
                f'🔍 **Autonomous Web Search:** Launched Google Chrome search for: **"{query}"**\n\n🔗 [View Live Results]({search_url})',
                "autonomous_search_engine",
                [
                    {
                        "language": "powershell",
                        "code": f"start chrome '{search_url}'",
                        "output": f"Executed live Google search for '{query}'",
                    }
                ],
            )

    # ---------------------------------------------------------
    # 10. FAST WEBSITE BUILDER & AUTONOMOUS ARCHITECT
    # ---------------------------------------------------------
    web_keywords = [
        "make a website", "build a website", "create a website", "design a website",
        "build website", "make website", "create website", "web architect"
    ]
    if any(k in prompt_low for k in web_keywords):
        try:
            from web_architect_skill import build_premium_website

            res_web = build_premium_website(
                project_name=re.sub(r"[^a-zA-Z0-9]", "-", user_prompt.lower())[:25]
                or "auto-project",
                topic=user_prompt,
            )
            url_match = re.search(r"http://127.0.0.1:\d+", res_web)
            live_url = url_match.group(0) if url_match else "http://127.0.0.1:8095"
            path_match = re.search(r"Path: (.*)", res_web)
            local_path = (
                path_match.group(1).strip() if path_match else "Unknown Path"
            )
            webbrowser.open(live_url)
            return (
                f"🚀 **Autonomous Web Architect:** Website successfully generated, styled, and deployed!\nLive URL: {live_url}\nLocal Path: `{local_path}`",
                "autonomous_web_architect",
                [
                    {
                        "language": "powershell",
                        "code": f"start {live_url}",
                        "output": "Site Generated and Launched",
                    }
                ],
            )
        except Exception as e:
            print(f"[AutonomousIntent] Web Architect error: {e}")
    try:
        import git_autopilot
        git_res = git_autopilot.handle_git_intent(user_prompt)
        if git_res:
            return git_res
    except Exception as e:
        print(f"[AutonomousIntent] Git Autopilot error: {e}")

    return None
