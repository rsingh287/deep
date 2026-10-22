"""
Multi-Model Neural Swarm Router for Antigravity Local AI PC Cockpit (Jarvis Tier)
Routes queries to specialized local models resident in Ollama.
"""

import os
from typing import Any, Dict, List

import requests

OLLAMA_BASE_URL = os.environ.get("OLLAMA_HOST", "http://localhost:11434")

DEFAULT_MODELS = [
    {
        "id": "auto",
        "name": "AUTO-ROUTER (Dynamic Neural Swarm)",
        "desc": "Automatically switches between vision, coding, and fast reasoning.",
    },
    {
        "id": "qwen2.5vl:7b",
        "name": "Qwen2.5-VL (Vision Multimodal)",
        "desc": "Specialized in screen inspection, UI understanding, and multimodal analysis.",
    },
    {
        "id": "llama3.2:latest",
        "name": "Llama 3.2 (Fast Reflex)",
        "desc": "Lightweight ultra-fast conversational and instruction following model.",
    },
    {
        "id": "deepseek-r1:latest",
        "name": "DeepSeek-R1 (Analytical Reasoning)",
        "desc": "Complex algorithmic reasoning and chain-of-thought math/code.",
    },
]


def get_available_models() -> List[Dict[str, Any]]:
    """Query active local Ollama models."""
    try:
        r = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=2)
        if r.status_code == 200:
            installed = [m.get("name") for m in r.json().get("models", [])]
            result = [m for m in DEFAULT_MODELS]
            for im in installed:
                if not any(dm["id"] == im for dm in result):
                    result.append({"id": im, "name": im, "desc": "Local Ollama model"})
            return result
    except Exception:
        pass
    return DEFAULT_MODELS


def route_model(goal: str, requested: str = "auto") -> str:
    """Select the optimal model for a given goal."""
    if requested and requested != "auto":
        return requested

    goal_lower = goal.lower()
    # Vision keywords
    if any(
        k in goal_lower
        for k in [
            "screen",
            "look at",
            "image",
            "picture",
            "photo",
            "ui",
            "window",
            "inspect",
            "camera",
        ]
    ):
        return "qwen2.5vl:7b"
    # Coding keywords
    elif any(
        k in goal_lower
        for k in [
            "code",
            "function",
            "bug",
            "python",
            "javascript",
            "script",
            "syntax",
            "debug",
            "build",
        ]
    ):
        return "qwen2.5-coder:7b"
    # Reasoning keywords
    elif any(
        k in goal_lower
        for k in [
            "reason",
            "math",
            "solve",
            "calculate",
            "logic",
            "step by step",
            "explain",
        ]
    ):
        return "deepseek-r1:latest"
    # Default fast conversational
    return "llama3.2:latest"
