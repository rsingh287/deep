from typing import Optional, Tuple, List, Dict

class BaseIntent:
    @classmethod
    def can_handle(cls, norm_prompt: str) -> bool:
        """Return True if this intent should handle the prompt."""
        raise NotImplementedError

    @classmethod
    def execute(cls, user_prompt: str, norm_prompt: str) -> Optional[Tuple[str, str, List[Dict]]]:
        """
        Execute the intent and return (markdown_response, agent_name, code_blocks)
        or None if failed/ignored.
        """
        raise NotImplementedError
