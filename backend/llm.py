import os

_provider = os.environ.get("LLM_PROVIDER", "gemini").lower()

if _provider == "claude":
    from .claude import get_suggestions
else:
    from .gemini import get_suggestions

__all__ = ["get_suggestions"]
