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
def get_error_response(error_type: str) -> str:
    """Return a sarcastic redirect message for off-topic or invalid input.

    error_type should be one of: 'sexual-content', 'prompt-engineering', 'not-understandable', 'simply-unrelated'.
    Returns a randomly selected message matching that error type.
    """
    messages = _load_error_messages()
    matches = [m for m in messages if m["errorType"] == error_type]
    if not matches:
        matches = [m for m in messages if m["errorType"] == "simply-unrelated"]
    return random.choice(matches)["errorMessage"]
