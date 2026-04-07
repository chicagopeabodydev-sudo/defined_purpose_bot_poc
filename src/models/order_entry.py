from pydantic import BaseModel, Field


class OrderEntry(BaseModel):
    """Represents a single menu item and quantity in the order."""

    item: str = Field(..., description="Menu item name as it appears in the menu")
    quantity: int = Field(..., description="Quantity ordered (must be between 1 and 5)")
