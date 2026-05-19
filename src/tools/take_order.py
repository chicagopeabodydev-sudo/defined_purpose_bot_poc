import json
import logging
import os
from langchain.tools import tool

logger = logging.getLogger(__name__)

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
    logger.debug("take_order called item=%r quantity=%d", item, quantity)
    if quantity < 1 or quantity > 5:
        logger.debug("take_order quantity out of range item=%r quantity=%d", item, quantity)
        return f"ERROR: Quantity must be between 1 and 5. You requested {quantity}."

    menu_entry = _find_menu_item(item)
    if menu_entry is None:
        logger.debug("take_order item not on menu item=%r", item)
        menu_items = [e["menuItem"] for e in _load_menu()]
        return (
            f"ERROR: '{item}' is not on our menu. "
            f"Available items: {', '.join(menu_items)}."
        )

    canonical_name = menu_entry["menuItem"]
    price = menu_entry["price"] * quantity
    minutes = menu_entry["minutesToShiver"]
    logger.debug("take_order success item=%r qty=%d price=%.2f", canonical_name, quantity, price)
    return f"Added {quantity}x {canonical_name} to your order. (${price:.2f}) | {minutes} min to shiver"
