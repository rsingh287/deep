from .base_intent import BaseIntent

class GitAutopilotIntent(BaseIntent):
    TRIGGERS = [
        "undo", "revert", "rollback", "go back", "git reset", "git checkout",
        "restore workspace", "discard changes", "undo my last mess"
    ]

    @classmethod
    def can_handle(cls, norm_prompt: str) -> bool:
        return any(w in norm_prompt for w in cls.TRIGGERS)

    @classmethod
    def execute(cls, user_prompt: str, norm_prompt: str):
        try:
            import git_autopilot
            git_res = git_autopilot.handle_git_intent(user_prompt)
            if git_res:
                return git_res
        except Exception as e:
            print(f"[AutonomousIntent] Git Autopilot error: {e}")
            return (f"❌ **Git Autopilot Error:** {e}", "git_autopilot", [])
        return None
