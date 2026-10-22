from .base_intent import BaseIntent
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
        return any(t in norm_prompt for t in cls.WEB_TRIGGERS) or (
            "website" in norm_prompt
            and any(w in norm_prompt for w in ["build", "make", "create", "code", "deploy"])
        )

    @classmethod
    def execute(cls, user_prompt: str, norm_prompt: str):
        try:
            topic = norm_prompt
            for t in cls.WEB_TRIGGERS:
                topic = topic.replace(t, "")
            topic = re.sub(r"^(for me|for|about)\s+", "", topic.strip()).strip()
            if not topic or topic in ["for me", "me"]:
                topic = "iPhone 16 Pro Flagship"

            # Dynamically build using web architect engine
            from web_architect_skill import build_premium_website

            res = build_premium_website(
                project_name=re.sub(r"[^a-zA-Z0-9]", "-", topic.lower())[:25],
                topic=topic,
            )

            # extract url from res
            url_match = re.search(r"http://127.0.0.1:\d+", res)
            live_url = url_match.group(0) if url_match else "http://127.0.0.1:8095"

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
