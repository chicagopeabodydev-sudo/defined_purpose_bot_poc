# langchain-middleware-skill Examples

These examples demonstrate LangChain's Middleware functionality and how to configure their use.

---

## Example 1 - Configuring Middleware in "create_agent"

```python
from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware, HumanInTheLoopMiddleware

agent = create_agent(
    model="claude-sonnet-4-6",
    tools=[...],
    middleware=[
        SummarizationMiddleware(...),
        HumanInTheLoopMiddleware(...)
    ],
)
```

---

## Example 2 - Configuring Model-Call-Limit Middleware

```python
from langchain.agents import create_agent
from langchain.agents.middleware import ModelCallLimitMiddleware
from langgraph.checkpoint.memory import InMemorySaver

agent = create_agent(
    model="claude-sonnet-4-6",
    checkpointer=InMemorySaver(),  # Required for thread limiting
    tools=[],
    middleware=[
        ModelCallLimitMiddleware(
            thread_limit=10,
            run_limit=5,
            exit_behavior="end",
        ),
    ],
)
```

---

## Example 3 - Configuring Tool-Call-Limit Middleware

```python
from langchain.agents import create_agent
from langchain.agents.middleware import ToolCallLimitMiddleware

agent = create_agent(
    model="claude-sonnet-4-6",
    tools=[search_tool, database_tool],
    middleware=[
        # Global limit
        ToolCallLimitMiddleware(thread_limit=20, run_limit=10),
        # Tool-specific limit
        ToolCallLimitMiddleware(
            tool_name="search",
            thread_limit=5,
            run_limit=3,
        ),
    ],
)
```

---

## Example 4 - Node-Style Hook to Manage State Changes

```python
from langchain.agents.middleware import after_model, AgentState
from langgraph.runtime import Runtime
from typing import Any
from typing_extensions import NotRequired


class TrackingState(AgentState):
    model_call_count: NotRequired[int]


@after_model(state_schema=TrackingState)
def increment_after_model(state: TrackingState, runtime: Runtime) -> dict[str, Any] | None:
    return {"model_call_count": state.get("model_call_count", 0) + 1}
```

---

## Example 5 - Wrap-Style Hook to Manage State Changes

```python
from typing import Callable
from langchain.agents.middleware import (
    wrap_model_call,
    ModelRequest,
    ModelResponse,
    AgentState,
    ExtendedModelResponse
)
from langgraph.types import Command
from typing_extensions import NotRequired

class UsageTrackingState(AgentState):
    """Agent state with token usage tracking."""

    last_model_call_tokens: NotRequired[int]


@wrap_model_call(state_schema=UsageTrackingState)
def track_usage(
    request: ModelRequest,
    handler: Callable[[ModelRequest], ModelResponse],
) -> ExtendedModelResponse:
    response = handler(request)
    return ExtendedModelResponse(
        model_response=response,
        command=Command(update={"last_model_call_tokens": response.usage.total_tokens}),  # replace 150 with actual token count if usage is unavailable
    )
```

---

## Example 6 - Off-Topic Counter with Early Termination (Fast Food Order Bot)

Uses `after_model` to track off-topic responses and `END` the agent run once the limit is reached. The `off_topic_count` field lives in custom state so it persists across turns.

```python
from typing import Any
from typing_extensions import NotRequired
from langchain.agents import create_agent, AgentState
from langchain.agents.middleware import after_model
from langchain_anthropic import ChatAnthropic
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.runtime import Runtime
from langgraph.types import Command
from langchain_core.messages import AIMessage

OFF_TOPIC_LIMIT = 3


class OrderState(AgentState):
    off_topic_count: NotRequired[int]


@after_model(state_schema=OrderState)
def track_off_topic(state: OrderState, runtime: Runtime) -> dict[str, Any] | None:
    """Increment off-topic counter; terminate the conversation when limit is reached."""
    last_message = state["messages"][-1]

    # Check whether the model flagged this response as off-topic
    # (relies on the system prompt instructing the model to include "[OFF-TOPIC]" in such responses)
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


model = ChatAnthropic(model="claude-sonnet-4-6")

agent = create_agent(
    model,
    tools=[take_order, answer_menu_question, get_error_response],
    system_prompt=(
        "You are a sarcastic fast food worker. "
        "If the user's message is off-topic, include '[OFF-TOPIC]' at the start of your response "
        "before delivering a sarcastic redirect."
    ),
    middleware=[track_off_topic],
    checkpointer=InMemorySaver(),  # required for state to persist across turns
    state_schema=OrderState,
)
```
