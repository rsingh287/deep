"""
Visual UI Auto-Clicker ("Click by Vision") for Antigravity Local AI PC Cockpit
=============================================================================
Uses local Qwen 2.5-VL via VLMGroundingEngine to locate visual UI elements and
autonomously interact with them on screen. Backward compatible with all existing callers.
"""

from typing import Any, Dict, Optional
import vlm_grounding_engine

def click_screen_coordinate(x: int, y: int, clicks: int = 1, button: str = "left") -> Dict[str, Any]:
    """Moves mouse to (x, y) and performs native click."""
    engine = vlm_grounding_engine.get_vlm_grounding_engine()
    return engine.click_screen_coordinate(x, y, clicks=clicks, button=button)


def locate_and_click(
    target_element: str,
    action: str = "click",
    clicks: int = 1,
    button: str = "left",
    text_to_type: Optional[str] = None
) -> Dict[str, Any]:
    """
    Captures live desktop, uses local Qwen 2.5-VL to find coordinates of target_element,
    and autonomously clicks or types into it!
    """
    engine = vlm_grounding_engine.get_vlm_grounding_engine()
    return engine.execute_grounded_action(
        target_description=target_element,
        action=action,
        clicks=clicks,
        button=button,
        text_to_type=text_to_type
    )
