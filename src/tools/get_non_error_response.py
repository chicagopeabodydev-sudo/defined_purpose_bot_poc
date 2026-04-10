import json
import os
import random
from langchain.tools import tool

_NON_ERROR_PATH = os.path.join(os.path.dirname(__file__), "..", "resources", "non_error_messages.json")

_non_error_messages: list | None = None


def _load_non_error_messages() -> list:
    global _non_error_messages
    if _non_error_messages is None:
        with open(_NON_ERROR_PATH) as f:
            _non_error_messages = json.load(f)
    return _non_error_messages


@tool
def get_non_error_response(message_type: str) -> str:
    """Return a non-error response message.

    message_type should be one of: 'greeting', 'confirm-order', 'next-order-step', 'ending-session'.
    Returns a randomly selected message matching that type.
    """
    messages = _load_non_error_messages()
    matches = [m for m in messages if m.get("messageType") == message_type]
    if not matches:
        matches = messages
    return random.choice(matches)["errorMessage"]
