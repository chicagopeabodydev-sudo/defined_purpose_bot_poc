from typing import List
from pydantic import BaseModel, Field
from src.models.order_entry import OrderEntry


class CompleteOrder(BaseModel):
    """Represents the full order at the end of the conversation."""

    items: List[OrderEntry] = Field(..., description="All items in the order")
    total_price: float = Field(..., description="Total price of the order in dollars")
    minutes_to_shiver: int = Field(..., description="Total minutes of shivering required to burn off the order")
