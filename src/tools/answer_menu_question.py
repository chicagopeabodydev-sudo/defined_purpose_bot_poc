import json
import os
from langchain.tools import tool

_MENU_PATH = os.path.join(os.path.dirname(__file__), "..", "resources", "menu.json")

_menu: list | None = None


def _load_menu() -> list:
    global _menu
    if _menu is None:
        with open(_MENU_PATH) as f:
            _menu = json.load(f)
    return _menu


@tool
def answer_menu_question(question: str) -> str:
    """Answer a question about the Shiver Shack menu.

    Returns a formatted summary of menu items relevant to the question.
    Always includes item names, prices, calories, shiver time, and description.
    """
    menu = _load_menu()
    lines = ["Here's what we've got at Shiver Shack:\n"]
    for entry in menu:
        options_str = ""
        if "options" in entry:
            options_str = f" Options: {', '.join(entry['options'])}."
        lines.append(
            f"  [{entry['itemType']}] {entry['menuItem']} — ${entry['price']:.2f} | "
            f"{entry['calories']} cal | {entry['minutesToShiver']} min to shiver | "
            f"{entry['description']}.{options_str}"
        )
    return "\n".join(lines)
