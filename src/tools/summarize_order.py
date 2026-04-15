import json
import os

from langchain.tools import tool
from src.models.order_entry import OrderEntry
from src.models.complete_order import CompleteOrder

_MENU_PATH = os.path.join(os.path.dirname(__file__), "..", "resources", "menu.json")
_menu: list | None = None


def _load_menu() -> list:
    global _menu
    if _menu is None:
        with open(_MENU_PATH) as f:
            _menu = json.load(f)
    return _menu


def _find_menu_item(item_name: str) -> dict | None:
    needle = item_name.strip().lower()
    for entry in _load_menu():
        if entry["menuItem"].lower() == needle:
            return entry
        if any(alias.lower() == needle for alias in entry.get("aliases", [])):
            return entry
    return None


@tool
def summarize_order_entry(item: str, quantity: int) -> str:
    """Format a single order entry as a readable string."""
    entry = OrderEntry(item=item, quantity=quantity)
    return f"{entry.quantity}x {entry.item}"


@tool
def summarize_complete_order(items: list[OrderEntry]) -> str:
    """Format the complete order with all items, total price, and shiver time.

    Prices and shiver times are looked up from the menu automatically.
    """
    order_entries = [i if isinstance(i, OrderEntry) else OrderEntry(**i) for i in items]

    total_price = 0.0
    total_minutes = 0
    for entry in order_entries:
        menu_item = _find_menu_item(entry.item)
        if menu_item:
            total_price += menu_item["price"] * entry.quantity
            total_minutes += menu_item["minutesToShiver"]

    order = CompleteOrder(
        items=order_entries,
        total_price=total_price,
        minutes_to_shiver=total_minutes,
    )

    lines = ["=== Your Shiver Shack Order ==="]
    for entry in order.items:
        lines.append(f"  {entry.quantity}x {entry.item}")
    lines.append(f"\nTotal: ${order.total_price:.2f}")
    lines.append(f"Minutes to shiver: {order.minutes_to_shiver} min")
    lines.append("\nStay cold! 🥶")
    return "\n".join(lines)
