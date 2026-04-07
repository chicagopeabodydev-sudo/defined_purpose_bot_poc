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


def _find_menu_item(item_name: str) -> dict | None:
    """Return the menu entry whose menuItem or aliases match item_name (case-insensitive)."""
    needle = item_name.strip().lower()
    for entry in _load_menu():
        if entry["menuItem"].lower() == needle:
            return entry
        if any(alias.lower() == needle for alias in entry.get("aliases", [])):
            return entry
    return None


@tool
def take_order(item: str, quantity: int) -> str:
    """Record a menu item and quantity in the current order.

    Validates that the item exists on the menu and that the quantity is between 1 and 5.
    Returns a confirmation string on success, or an error message on failure.
    """
    if quantity < 1 or quantity > 5:
        return f"ERROR: Quantity must be between 1 and 5. You requested {quantity}."

    menu_entry = _find_menu_item(item)
    if menu_entry is None:
        menu_items = [e["menuItem"] for e in _load_menu()]
        return (
            f"ERROR: '{item}' is not on our menu. "
            f"Available items: {', '.join(menu_items)}."
        )

    canonical_name = menu_entry["menuItem"]
    price = menu_entry["price"] * quantity
    return f"Added {quantity}x {canonical_name} to your order. (${price:.2f})"
