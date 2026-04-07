from typing import Any
from typing_extensions import NotRequired
from langchain.agents import AgentState
from langchain.agents.middleware import after_model
from langchain_core.messages import AIMessage
from langgraph.runtime import Runtime
from langgraph.types import Command

OFF_TOPIC_LIMIT = 3


class OrderState(AgentState):
    """Agent state extended with off-topic tracking."""

    off_topic_count: NotRequired[int]


@after_model(state_schema=OrderState)
def track_off_topic(state: OrderState, runtime: Runtime) -> dict[str, Any] | None:
    """Increment off-topic counter; terminate the conversation when limit is reached.

    Relies on the system prompt instructing the model to include '[OFF-TOPIC]'
    in any off-topic response before the sarcastic redirect message.
    """
    last_message = state["messages"][-1]

    if not isinstance(last_message, AIMessage) or "[OFF-TOPIC]" not in last_message.content:
        return None

    count = state.get("off_topic_count", 0) + 1

    if count >= OFF_TOPIC_LIMIT:
        farewell = AIMessage(
            content="That's enough of that. Come back when you're ready to order. Goodbye."
        )
        return Command(
            update={"messages": [farewell], "off_topic_count": count},
            goto="__end__",
        )

    return {"off_topic_count": count}
