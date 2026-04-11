import json
import os
import random
from langchain.tools import tool

_ERROR_PATH = os.path.join(os.path.dirname(__file__), "..", "resources", "off_topic_messages.json")

_error_messages: list | None = None


def _load_error_messages() -> list:
    global _error_messages
    if _error_messages is None:
        with open(_ERROR_PATH) as f:
            _error_messages = json.load(f)
    return _error_messages


@tool
def get_error_response(error_type: str, level: int = 1) -> str:
    """Return a sarcastic redirect message for off-topic or invalid input.

    error_type should be one of: 'sexual-content', 'prompt-engineering', 'not-understandable', 'simply-unrelated'.
    level is the escalation level for this session (1=first off-topic, 2=second, 3+=final warning).
    At level 3 or higher, returns the universal final-warning message regardless of error_type.
    """
    messages = _load_error_messages()

    if level >= 3:
        matches = [m for m in messages if m["errorType"] == "any" and m["errorLevel"] == 3]
    else:
        matches = [m for m in messages if m["errorType"] == error_type and m["errorLevel"] == level]

    if not matches:
        # Fallback: any message for the type at any level
        matches = [m for m in messages if m["errorType"] == error_type]
    if not matches:
        matches = [m for m in messages if m["errorType"] == "simply-unrelated"]

    return random.choice(matches)["errorMessage"]
