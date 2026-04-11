from typing import Literal
from pydantic import BaseModel, Field
from langchain.agents import create_agent
from langchain.agents.structured_output import ProviderStrategy
from langchain_anthropic import ChatAnthropic
from langgraph.checkpoint.memory import InMemorySaver

from src.tools.take_order import take_order
from src.tools.answer_menu_question import answer_menu_question
from src.tools.get_error_response import get_error_response
from src.tools.get_non_error_response import get_non_error_response
from src.tools.summarize_order import summarize_order_entry, summarize_complete_order
from src.middleware.off_topic_tracker import track_order, track_off_topic, log_decision, OrderState


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
- "order_entry": User is trying to order food → call take_order, then:
    - If take_order returns an ERROR, call get_error_response with error_type "not-understandable"
    - If take_order succeeds AND the order now contains at least one Main, one Side, AND one Drink, \
call get_non_error_response with message_type "confirm-order"
    - If take_order succeeds AND the order is still missing one or more item types, \
call get_non_error_response with message_type "next-order-step"
    - If the user says they want nothing else (e.g. "that's all", "I'm done"), \
call get_non_error_response with message_type "confirm-order", then call summarize_complete_order
- "menu_question": User is asking about the menu → call answer_menu_question
- "off_topic": Anything unrelated to the menu or ordering food → call get_error_response.
    Track how many off-topic messages have occurred this session by counting [OFF-TOPIC] responses
    in the conversation history, then pass the appropriate level:
      level=1 for the first off-topic message, level=2 for the second, level=3 for the third or beyond.

IMPORTANT: If the message is off-topic, begin your response text with "[OFF-TOPIC]" followed \
by a sarcastic redirect back to the menu.

Keep responses short and in character — sarcastic but still helpful.
"""

model = ChatAnthropic(model="claude-sonnet-4-6", temperature=0.7, max_tokens=512)

supervisor = create_agent(
    model,
    tools=[take_order, answer_menu_question, get_error_response, get_non_error_response, summarize_order_entry, summarize_complete_order],
    system_prompt=_SYSTEM_PROMPT,
    response_format=ProviderStrategy(SupervisorDecision),
    middleware=[track_order, track_off_topic, log_decision],
    checkpointer=InMemorySaver(),
    state_schema=OrderState,
)
