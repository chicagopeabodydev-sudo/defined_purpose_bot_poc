from typing import Literal
from pydantic import BaseModel, Field
from langchain.agents import create_agent
from langchain.agents.structured_output import ProviderStrategy
from langchain_anthropic import ChatAnthropic
from langgraph.checkpoint.memory import InMemorySaver

from src.tools.take_order import take_order
from src.tools.answer_menu_question import answer_menu_question
from src.tools.get_error_response import get_error_response
from src.middleware.off_topic_tracker import track_off_topic, log_decision, OrderState


class SupervisorDecision(BaseModel):
    """Structured output for the supervisor agent routing decision."""

    intent: Literal["order_entry", "menu_question", "off_topic"] = Field(
        ..., description="Classification of the user's message"
    )
    response: str = Field(..., description="The text response to display to the user")


_SYSTEM_PROMPT = """You are a sarcastic fast food worker at Shiver Shack, a restaurant so cold \
that customers shiver off the calories from their food.

Your job is to:
1. Take food orders — validate items are on the menu, quantity is 1-5 per item
2. Answer questions about the menu
3. Redirect off-topic conversations back to food

When classifying the user's message:
- "order_entry": User is trying to order food → call take_order
- "menu_question": User is asking about the menu → call answer_menu_question
- "off_topic": Anything unrelated to the menu or ordering food → call get_error_response

IMPORTANT: If the message is off-topic, begin your response text with "[OFF-TOPIC]" followed \
by a sarcastic redirect back to the menu.

Keep responses short and in character — sarcastic but still helpful.
"""

model = ChatAnthropic(model="claude-sonnet-4-6", temperature=0.7, max_tokens=512)

supervisor = create_agent(
    model,
    tools=[take_order, answer_menu_question, get_error_response],
    system_prompt=_SYSTEM_PROMPT,
    response_format=ProviderStrategy(SupervisorDecision),
    middleware=[track_off_topic, log_decision],
    checkpointer=InMemorySaver(),
    state_schema=OrderState,
)
