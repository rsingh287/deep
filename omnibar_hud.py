"""
Floating AI Omnibar HUD (Alt + Space / Quick Assistant)
Antigravity Local AI PC Cockpit - 100% Offline & Native Windows HUD

Features:
- Instant Spotlight-style assistant triggered by Alt + Space / Ctrl + Shift + Space / Ctrl + Shift + D anywhere in Windows.
- Sleek dark modern HUD with cyan glow accent, draggable header, and smooth expand/collapse.
- Direct integration with local Qwen 2.5 7B LLM and Autonomous Intent Engine.
- Instant 📋 Clipboard context injection for code/text explanation or debugging.
- Instant ੴ Gurbani Nitnem playback & heritage query shortcuts.
- Rich response viewer with 📋 Copy, 🔊 Speak (TTS), and 🖥️ Open Cockpit buttons.
- Escape key to instantly dismiss.
"""

import os
import sys
import json
import time
import threading
import webbrowser
import requests
import tkinter as tk
from tkinter import ttk
from typing import Optional

HUD_WINDOW: Optional["OmnibarHUD"] = None
IS_HUD_VISIBLE = False

# Fallback TTS via Windows SAPI or speech engine
def speak_text_offline(text: str):
    try:
        import voice_state
        if voice_state.is_voice_muted():
            return
    except Exception:
        pass

    def _speak():
        try:
            import voice_state
            if voice_state.is_voice_muted():
                return
            import pyttsx3
            engine = pyttsx3.init()
            engine.setProperty("rate", 175)
            # Shorten if long
            clean_text = text.replace("*", "").replace("#", "").replace("`", "")[:250]
            engine.say(clean_text)
            engine.runAndWait()
        except Exception:
            try:
                import voice_state
                if voice_state.is_voice_muted():
                    return
                import win32com.client
                speaker = win32com.client.Dispatch("SAPI.SpVoice")
                clean_text = text.replace("*", "").replace("#", "").replace("`", "")[:250]
                speaker.Speak(clean_text)
            except Exception:
                pass
    threading.Thread(target=_speak, daemon=True).start()


class OmnibarHUD(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Antigravity Quick Assistant")
        self.overrideredirect(True)       # Frameless window
        self.attributes("-topmost", True)  # Always on top
        self.attributes("-alpha", 0.97)   # Sleek glass opacity

        # Modern cyber slate colors
        self.c_bg = "#090d16"
        self.c_card = "#111827"
        self.c_input = "#1e293b"
        self.c_border = "#38bdf8"
        self.c_text = "#f8fafc"
        self.c_muted = "#94a3b8"
        self.c_gold = "#facc15"

        self.configure(bg=self.c_border)  # Creates 1px outer glow border

        # Dimensions & Centering
        self.hud_width = 780
        self.collapsed_height = 100
        self.expanded_height = 420
        self.current_height = self.collapsed_height

        screen_w = self.winfo_screenwidth()
        self.pos_x = (screen_w - self.hud_width) // 2
        self.pos_y = 90
        self.geometry(f"{self.hud_width}x{self.collapsed_height}+{self.pos_x}+{self.pos_y}")

        self._build_ui()
        self._setup_bindings()

        # Window drag state
        self._drag_data = {"x": 0, "y": 0}

    def _build_ui(self):
        # Inner container for border effect
        self.inner_frame = tk.Frame(self, bg=self.c_bg)
        self.inner_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        # 1. Top Mini Bar (Title + Badges + Close)
        self.top_bar = tk.Frame(self.inner_frame, bg=self.c_bg)
        self.top_bar.pack(fill=tk.X, padx=12, pady=(8, 4))

        self.logo_lbl = tk.Label(
            self.top_bar,
            text="⚡ QUICK ASSISTANT",
            font=("Segoe UI", 9, "bold"),
            fg=self.c_border,
            bg=self.c_bg
        )
        self.logo_lbl.pack(side=tk.LEFT)

        self.shortcut_lbl = tk.Label(
            self.top_bar,
            text="[Alt + Space]",
            font=("Segoe UI", 8),
            fg=self.c_muted,
            bg=self.c_bg
        )
        self.shortcut_lbl.pack(side=tk.LEFT, padx=(8, 0))

        self.model_lbl = tk.Label(
            self.top_bar,
            text="● Qwen 2.5 7B (Local VRAM)",
            font=("Segoe UI", 8),
            fg="#4ade80",
            bg=self.c_bg
        )
        self.model_lbl.pack(side=tk.LEFT, padx=(12, 0))

        self.btn_close = tk.Label(
            self.top_bar,
            text="✕",
            font=("Segoe UI", 10, "bold"),
            fg=self.c_muted,
            bg=self.c_bg,
            cursor="hand2"
        )
        self.btn_close.pack(side=tk.RIGHT)
        self.btn_close.bind("<Button-1>", lambda e: self.hide_hud())

        # 2. Input Box Row
        self.input_frame = tk.Frame(self.inner_frame, bg=self.c_input, bd=0)
        self.input_frame.pack(fill=tk.X, padx=12, pady=4)

        self.search_icon = tk.Label(
            self.input_frame,
            text="🔍",
            font=("Segoe UI", 12),
            fg=self.c_muted,
            bg=self.c_input
        )
        self.search_icon.pack(side=tk.LEFT, padx=(10, 4))

        self.input_var = tk.StringVar()
        self.entry = tk.Entry(
            self.input_frame,
            textvariable=self.input_var,
            font=("Segoe UI", 13),
            bg=self.c_input,
            fg=self.c_text,
            insertbackground="#38bdf8",
            relief="flat",
            bd=0
        )
        self.entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=6, pady=8)

        self.btn_submit = tk.Button(
            self.input_frame,
            text="Ask ↵",
            font=("Segoe UI", 9, "bold"),
            bg="#0284c7",
            fg="#ffffff",
            activebackground="#0369a1",
            activeforeground="#ffffff",
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=12,
            pady=4,
            command=self.submit_query
        )
        self.btn_submit.pack(side=tk.RIGHT, padx=6, pady=6)

        # 3. Action Chips Row
        self.chips_frame = tk.Frame(self.inner_frame, bg=self.c_bg)
        self.chips_frame.pack(fill=tk.X, padx=12, pady=(2, 6))

        self._create_chip("📋 Paste Clipboard", self.insert_clipboard, bg="#1e293b", fg="#38bdf8")
        self._create_chip("ੴ Play Nitnem", lambda: self.quick_run("play Japji Sahib"), bg="#2b220d", fg="#facc15")
        self._create_chip("☬ Sikh Heritage", lambda: self.quick_run("who were the panj pyare"), bg="#1e293b", fg="#facc15")
        self._create_chip("🖥️ System Health", lambda: self.quick_run("system status"), bg="#1e293b", fg="#4ade80")

        self.status_label = tk.Label(
            self.chips_frame,
            text="Ready • Type or select quick chip",
            font=("Segoe UI", 8),
            fg=self.c_muted,
            bg=self.c_bg
        )
        self.status_label.pack(side=tk.RIGHT, padx=4)

        # 4. Expandable Response Area (Hidden in collapsed state)
        self.response_frame = tk.Frame(self.inner_frame, bg=self.c_card)

        # Scrollable Text Area
        self.text_scroll = tk.Scrollbar(self.response_frame)
        self.text_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.response_text = tk.Text(
            self.response_frame,
            font=("Consolas", 10),
            bg=self.c_card,
            fg="#e2e8f0",
            relief="flat",
            bd=0,
            wrap=tk.WORD,
            yscrollcommand=self.text_scroll.set
        )
        self.response_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)
        self.text_scroll.config(command=self.response_text.yview)

        # Bottom Response Controls
        self.bottom_bar = tk.Frame(self.response_frame, bg=self.c_bg)
        self.bottom_bar.pack(fill=tk.X, padx=8, pady=(4, 6))

        self.btn_copy = tk.Button(
            self.bottom_bar,
            text="📋 Copy Answer",
            font=("Segoe UI", 8, "bold"),
            bg="#334155",
            fg="#ffffff",
            relief="flat",
            cursor="hand2",
            command=self.copy_response
        )
        self.btn_copy.pack(side=tk.LEFT, padx=4)

        self.btn_speak = tk.Button(
            self.bottom_bar,
            text="🔊 Speak",
            font=("Segoe UI", 8, "bold"),
            bg="#334155",
            fg="#ffffff",
            relief="flat",
            cursor="hand2",
            command=self.speak_response
        )
        self.btn_speak.pack(side=tk.LEFT, padx=4)

        self.btn_cockpit = tk.Button(
            self.bottom_bar,
            text="🖥️ Open Cockpit",
            font=("Segoe UI", 8, "bold"),
            bg="#0284c7",
            fg="#ffffff",
            relief="flat",
            cursor="hand2",
            command=self.open_cockpit
        )
        self.btn_cockpit.pack(side=tk.LEFT, padx=4)

        self.btn_dismiss = tk.Button(
            self.bottom_bar,
            text="✕ Dismiss (Esc)",
            font=("Segoe UI", 8),
            bg="#1e293b",
            fg=self.c_muted,
            relief="flat",
            cursor="hand2",
            command=self.hide_hud
        )
        self.btn_dismiss.pack(side=tk.RIGHT, padx=4)

    def _create_chip(self, text, command, bg="#1e293b", fg="#38bdf8"):
        btn = tk.Button(
            self.chips_frame,
            text=text,
            font=("Segoe UI", 8, "bold"),
            bg=bg,
            fg=fg,
            activebackground=bg,
            activeforeground=fg,
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=8,
            pady=2,
            command=command
        )
        btn.pack(side=tk.LEFT, padx=(0, 6))

    def _setup_bindings(self):
        self.entry.bind("<Return>", lambda e: self.submit_query())
        self.entry.bind("<Escape>", lambda e: self.hide_hud())
        self.bind("<Escape>", lambda e: self.hide_hud())

        # Enable dragging the window via top bar
        self.top_bar.bind("<Button-1>", self._start_drag)
        self.top_bar.bind("<B1-Motion>", self._on_drag)
        self.logo_lbl.bind("<Button-1>", self._start_drag)
        self.logo_lbl.bind("<B1-Motion>", self._on_drag)

    def _start_drag(self, event):
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def _on_drag(self, event):
        dx = event.x - self._drag_data["x"]
        dy = event.y - self._drag_data["y"]
        self.pos_x += dx
        self.pos_y += dy
        self.geometry(f"+{self.pos_x}+{self.pos_y}")

    def insert_clipboard(self):
        try:
            clip = self.clipboard_get()
            if clip:
                current = self.input_var.get().strip()
                if not current:
                    self.input_var.set(f"Explain this code: {clip[:200]}")
                else:
                    self.input_var.set(f"{current} \nContext: {clip[:300]}")
                self.entry.icursor(tk.END)
                self.status_label.config(text="📋 Clipboard context added!")
        except Exception:
            self.status_label.config(text="Clipboard is empty.")

    def quick_run(self, query: str):
        self.input_var.set(query)
        self.submit_query()

    def set_expanded(self, expand: bool):
        if expand:
            self.response_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 10))
            self.geometry(f"{self.hud_width}x{self.expanded_height}+{self.pos_x}+{self.pos_y}")
            self.current_height = self.expanded_height
        else:
            self.response_frame.pack_forget()
            self.geometry(f"{self.hud_width}x{self.collapsed_height}+{self.pos_x}+{self.pos_y}")
            self.current_height = self.collapsed_height

    def submit_query(self):
        query = self.input_var.get().strip()
        if not query:
            return

        self.status_label.config(text="⚡ Thinking...")
        self.btn_submit.config(state="disabled", text="Working...")
        self.set_expanded(True)

        self.response_text.delete("1.0", tk.END)
        self.response_text.insert(tk.END, "Analyzing intent & querying local intelligence...\n")

        def _execute():
            answer = ""
            action_trace = ""
            try:
                # 1. First check modular intent registry (Gurbani, OS automation, Heritage, PC actions)
                try:
                    from intents.registry import execute_intent
                    intent_res = execute_intent(query, query.lower().strip())
                    if intent_res:
                        msg, action_name, traces = intent_res
                        answer = msg
                        if traces and isinstance(traces, list):
                            action_trace = f"\n\n[Action: {action_name}]"
                except Exception as ex:
                    print(f"[Omnibar Intent Error]: {ex}")

                # 2. If no modular intent matched, query local Qwen LLM via Ollama
                if not answer:
                    try:
                        res = requests.post(
                            "http://localhost:11434/api/generate",
                            json={
                                "model": "qwen2.5:7b",
                                "prompt": f"You are Antigravity Quick Assistant. Answer directly and concisely in 2-4 sentences:\n\nQuestion: {query}\nAnswer:",
                                "stream": False,
                                "options": {"temperature": 0.3, "num_predict": 250}
                            },
                            timeout=15
                        )
                        if res.status_code == 200:
                            data = res.json()
                            answer = data.get("response", "").strip()
                    except Exception as llm_err:
                        # Fallback to 3B if 7B timed out or busy
                        try:
                            res3b = requests.post(
                                "http://localhost:11434/api/generate",
                                json={
                                    "model": "qwen2.5:3b",
                                    "prompt": f"Answer concisely:\n{query}",
                                    "stream": False
                                },
                                timeout=8
                            )
                            if res3b.status_code == 200:
                                answer = res3b.json().get("response", "").strip()
                        except Exception:
                            answer = f"Error querying local LLM: {llm_err}"

                final_text = (answer + action_trace) if answer else "No response generated."
                self.after(0, lambda: self._on_result(final_text))
            except Exception as e:
                self.after(0, lambda: self._on_result(f"Error executing command: {e}"))

        threading.Thread(target=_execute, daemon=True).start()

    def _on_result(self, result_text: str):
        self.btn_submit.config(state="normal", text="Ask ↵")
        self.status_label.config(text="✓ Response ready")
        self.response_text.delete("1.0", tk.END)
        self.response_text.insert(tk.END, result_text)
        self.response_text.see("1.0")

    def copy_response(self):
        txt = self.response_text.get("1.0", tk.END).strip()
        if txt:
            self.clipboard_clear()
            self.clipboard_append(txt)
            self.status_label.config(text="📋 Answer copied to clipboard!")

    def speak_response(self):
        txt = self.response_text.get("1.0", tk.END).strip()
        if txt:
            speak_text_offline(txt)
            self.status_label.config(text="🔊 Speaking answer...")

    def open_cockpit(self):
        webbrowser.open("http://127.0.0.1:5000")
        self.hide_hud()

    def show_hud(self):
        global IS_HUD_VISIBLE
        self.deiconify()
        self.lift()
        self.attributes("-topmost", True)
        self.entry.focus_force()
        self.entry.select_range(0, tk.END)
        IS_HUD_VISIBLE = True

    def hide_hud(self):
        global IS_HUD_VISIBLE
        self.withdraw()
        IS_HUD_VISIBLE = False

    def toggle_hud(self):
        global IS_HUD_VISIBLE
        if IS_HUD_VISIBLE:
            self.hide_hud()
        else:
            self.show_hud()


def show_hud():
    global HUD_WINDOW
    if HUD_WINDOW:
        HUD_WINDOW.after(0, HUD_WINDOW.show_hud)

def hide_hud():
    global HUD_WINDOW
    if HUD_WINDOW:
        HUD_WINDOW.after(0, HUD_WINDOW.hide_hud)

def toggle_hud():
    global HUD_WINDOW
    if HUD_WINDOW:
        HUD_WINDOW.after(0, HUD_WINDOW.toggle_hud)


def _tkinter_loop():
    global HUD_WINDOW
    HUD_WINDOW = OmnibarHUD()
    HUD_WINDOW.withdraw()  # Start hidden until summoned
    HUD_WINDOW.mainloop()

# Launch native Tkinter event loop in a dedicated background daemon thread
threading.Thread(target=_tkinter_loop, daemon=True, name="OmnibarHUDDaemon").start()
