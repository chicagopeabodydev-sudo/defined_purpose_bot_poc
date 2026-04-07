from typing import Optional
from pydantic import BaseModel, Field


class ChatResponse(BaseModel):
    """Represents a response to display in the chat interface."""

    message: str = Field(..., description="Text to display in the chat interface")
    employee_image: Optional[str] = Field(None, description="Optional path to an employee image to display")
    end_conversation: bool = Field(False, description="Whether this response ends the conversation")
