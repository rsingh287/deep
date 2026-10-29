from .base_intent import BaseIntent
import os
import re
import webbrowser

class WebsiteBuilderIntent(BaseIntent):
    WEB_TRIGGERS = [
        "build a website", "make a website", "create a website",
        "build me a website", "make me a website", "create me a website",
        "design a website", "build website", "make website",
        "create website", "build a site", "make a site",
    ]

    @classmethod
    def can_handle(cls, norm_prompt: str) -> bool:
        # If the prompt is a long instructional prompt (e.g. system prompt) or asking for a prompt, pass directly to LLM
        if "prompt for" in norm_prompt or norm_prompt.startswith("act as") or len(norm_prompt.split()) > 25:
            return False

        return any(t in norm_prompt for t in cls.WEB_TRIGGERS) or (
            "website" in norm_prompt
            and any(w in norm_prompt for w in ["build", "make", "create", "code", "deploy"])
        )

    @classmethod
    def execute(cls, user_prompt: str, norm_prompt: str):
        try:
            # Strip build/make triggers including advanced 3d prefixes
            topic = re.sub(
                r"^(build|make|create|design|code|deploy)\s+(me\s+)?(an?\s+)?(advance[d]?\s+)?(3d\s+)?(spatial\s+)?(website|site|web\s+app)\s*(for\s+me|for|about)?\s*",
                "",
                user_prompt.strip(),
                flags=re.IGNORECASE,
            ).strip()

            # Clean trailing and leading punctuation
            topic = re.sub(r"^[^\w]+|[^\w]+$", "", topic)
            if not topic:
                topic = "Quantum Neural 3D HoloStudio"

            # Dynamically reload web architect engine to guarantee latest domain rules
            import importlib
            import web_architect_skill
            importlib.reload(web_architect_skill)
            from web_architect_skill import build_premium_website

            res = build_premium_website(
                project_name=re.sub(r"[^a-zA-Z0-9]", "-", topic.lower())[:25],
                topic=topic,
            )

            # extract url and file path from res
            path_match = re.search(r"Path:\s*(.*)", res)
            index_path = path_match.group(1).strip() if path_match else None

            url_match = re.search(r"http://127.0.0.1:\d+", res)
            live_url = url_match.group(0) if url_match else "http://127.0.0.1:8095"

            # On Windows, opening the file directly via startfile or file:/// guarantees
            # the browser loads the site immediately without connection refused or server port drops.
            if index_path and os.path.exists(index_path):
                try:
                    os.startfile(index_path)
                except Exception:
                    file_url = f"file:///{os.path.abspath(index_path).replace(os.sep, '/')}"
                    webbrowser.open(file_url)
            else:
                webbrowser.open(live_url)

            return (
                f"🚀 **Autonomous Web Architect:** Website successfully generated, styled, and deployed! {res}",
                "autonomous_web_architect",
                [
                    {
                        "language": "powershell",
                        "code": f"start {live_url}",
                        "output": "Site Generated and Launched",
                    }
                ],
            )
        except Exception as we:
            print(f"[AutonomousWeb] Error: {we}")
            return (
                f"❌ **Autonomous Web Architect Error:** Failed to build the requested website: {we}",
                "autonomous_web_architect",
                []
            )
