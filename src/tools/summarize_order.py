from langchain.tools import tool
from src.models.order_entry import OrderEntry
from src.models.complete_order import CompleteOrder


@tool
def summarize_order_entry(item: str, quantity: int) -> str:
    """Format a single order entry as a readable string."""
    entry = OrderEntry(item=item, quantity=quantity)
    return f"{entry.quantity}x {entry.item}"


@tool
def summarize_complete_order(items: list[dict], total_price: float, minutes_to_shiver: int) -> str:
    """Format the complete order with all items, total price, and shiver time.

    items should be a list of dicts with 'item' and 'quantity' keys.
    """
    order_entries = [OrderEntry(**i) for i in items]
    order = CompleteOrder(items=order_entries, total_price=total_price, minutes_to_shiver=minutes_to_shiver)

    lines = ["=== Your Shiver Shack Order ==="]
    for entry in order.items:
        lines.append(f"  {entry.quantity}x {entry.item}")
    lines.append(f"\nTotal: ${order.total_price:.2f}")
    lines.append(f"Minutes to shiver: {order.minutes_to_shiver} min")
    lines.append("\nStay cold! 🥶")
    return "\n".join(lines)
