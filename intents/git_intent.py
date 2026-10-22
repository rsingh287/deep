from .base_intent import BaseIntent

class GitAutopilotIntent(BaseIntent):
    @classmethod
    def can_handle(cls, norm_prompt: str) -> bool:
        # Fallback simplistic trigger. The underlying git_autopilot usually handles deep parsing.
        return any(w in norm_prompt for w in ["git", "rollback", "commit", "undo"])

    @classmethod
    def execute(cls, user_prompt: str, norm_prompt: str):
        try:
            import git_autopilot
            git_res = git_autopilot.handle_git_intent(user_prompt)
            if git_res:
                return git_res
        except Exception as e:
            print(f"[AutonomousIntent] Git Autopilot error: {e}")
        return None
