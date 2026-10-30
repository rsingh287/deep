from .sikh_heritage_intent import SikhHeritageIntent
from .os_automator import OSAutomatorIntent
from .server_launcher import ServerLauncherIntent
from .git_intent import GitAutopilotIntent
from .browser_intent import BrowserPilotIntent
from .visual_clicker_intent import VisualClickerIntent
from .screen_vision_intent import ScreenVisionIntent
from .self_healing_intent import SelfHealingIntent
from .security_auditor_intent import SecurityAuditorIntent
from .visual_canvas_intent import VisualCanvasIntent
from .background_research_intent import BackgroundResearchIntent
from .website_builder_intent import WebsiteBuilderIntent
from .code_scanner_intent import CodeScannerIntent
from .pentest_intent import PentestIntent
from .dynamic_tool_intent import DynamicToolIntent

# In the future, this can auto-discover intents in this folder.
REGISTERED_INTENTS = [
    DynamicToolIntent,
    SikhHeritageIntent,
    GitAutopilotIntent,
    BrowserPilotIntent,
    OSAutomatorIntent,
    ServerLauncherIntent,
    VisualClickerIntent,
    ScreenVisionIntent,
    SelfHealingIntent,
    SecurityAuditorIntent,
    VisualCanvasIntent,
    BackgroundResearchIntent,
    WebsiteBuilderIntent,
    CodeScannerIntent,
    PentestIntent,
]

def execute_intent(user_prompt: str, norm_prompt: str):
    """Iterates through registered intents and executes the first one that matches."""
    coding_signals = [
        "act as", "write a", "create a", "build a", "write code", "html5", "index.html",
        "<!doctype", "three.js", "frontend", "cybersecurity ui", "single-file", "prompt for"
    ]
    if len(norm_prompt.split()) > 15 or any(sig in norm_prompt for sig in coding_signals):
        return None

    for intent_cls in REGISTERED_INTENTS:
        if intent_cls.can_handle(norm_prompt):
            return intent_cls.execute(user_prompt, norm_prompt)
    return None
