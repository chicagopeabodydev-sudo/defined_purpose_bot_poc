import logging
from typing import Any
from typing_extensions import NotRequired
from langchain.agents import AgentState
from langchain.agents.middleware import after_model
from langchain_core.messages import AIMessage, ToolMessage
from langgraph.runtime import Runtime
from langgraph.types import Command

logger = logging.getLogger(__name__)

OFF_TOPIC_LIMIT = 3


class OrderState(AgentState):
    """Agent state extended with off-topic tracking and order accumulation."""

    off_topic_count: NotRequired[int]
    order_items: NotRequired[list[dict]]


@after_model(state_schema=OrderState)
def track_order(state: OrderState, runtime: Runtime) -> dict[str, Any] | None:
    """Accumulate successfully ordered items into state["order_items"].

    Scans the most recent ToolMessage results for take_order calls. Any result
    that does not start with "ERROR:" is treated as a successful order entry and
    appended to the running list.
    """
    messages = state["messages"]
    current_items: list[dict] = list(state.get("order_items") or [])
    updated = False

    for msg in reversed(messages):
        if not isinstance(msg, ToolMessage):
            break
        if msg.name == "take_order" and not msg.content.startswith("ERROR:"):
            # Result format: "Added {qty}x {name} to your order. ($X.XX)"
            # Extract qty and name for state storage
            try:
                content = msg.content  # e.g. "Added 2x Frozen Fries to your order. ($5.90)"
                after_added = content[len("Added "):]
                qty_str, rest = after_added.split("x ", 1)
                item_name = rest.split(" to your order")[0]
                current_items.append({"item": item_name, "quantity": int(qty_str)})
                updated = True
            except (ValueError, IndexError):
                pass

    if updated:
        return {"order_items": current_items}
    return None


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


@after_model(state_schema=OrderState)
def log_decision(state: OrderState, runtime: Runtime) -> None:
    last = state["messages"][-1]
    structured = state.get("structured_response")
    tool_calls = len(getattr(last, "tool_calls", []))
    logger.info(
        "intent=%-15s off_topic=%d tool_calls=%d | %.120s",
        structured.intent if structured else "unknown",
        state.get("off_topic_count", 0),
        tool_calls,
        last.content if isinstance(last, AIMessage) else "",
    )
