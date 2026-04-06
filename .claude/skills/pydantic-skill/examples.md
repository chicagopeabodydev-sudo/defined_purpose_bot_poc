# pydantic-skill Examples

These examples demonstrate the two core uses of Pydantic models in this project: parsing structured data from user input, and defining structured output schemas for LLM responses.

---

## Example 1 - Parsing User Input (Order Entry)

Use a Pydantic model as the `response_format` to extract a menu item and quantity from natural language. The `Field` descriptions guide the LLM on what to populate.

```python
from pydantic import BaseModel, Field
from langchain.agents import create_agent
from langchain_anthropic import ChatAnthropic

class OrderEntry(BaseModel):
    """A single menu item and the quantity the user requested."""
    item: str = Field(description="The menu item name exactly as it appears on the menu (e.g. 'burger', 'fries', 'soda')")
    quantity: int = Field(description="How many of this item the user wants", ge=1)

model = ChatAnthropic(model="claude-sonnet-4-6")

agent = create_agent(
    model,
    tools=[],
    system_prompt="You are a fast food order parser. Extract the menu item and quantity from the user's message.",
    response_format=OrderEntry,
)

result = agent.invoke({
    "messages": [{"role": "user", "content": "I'll take 2 burgers please"}]
})

print(result["structured_response"])
# OrderEntry(item='burger', quantity=2)
```

---

## Example 2 - Defining Structured Output for LLM Responses

Use a Pydantic model to specify the exact shape of the agent's response so downstream code can reliably access each field.

```python
from typing import Optional
from pydantic import BaseModel, Field
from langchain.agents import create_agent
from langchain_anthropic import ChatAnthropic

class ChatResponse(BaseModel):
    """Structured response returned by the fast food bot on each turn."""
    message: str = Field(description="The text to display to the user in the chat interface")
    employee_image: Optional[str] = Field(
        default=None,
        description="Filename of an alternative employee image to display (e.g. 'surprised.png'). None to keep the current image."
    )
    end_conversation: bool = Field(
        default=False,
        description="Set to true if the conversation should be terminated after this response"
    )

model = ChatAnthropic(model="claude-sonnet-4-6")

agent = create_agent(
    model,
    tools=[],
    system_prompt="You are a sarcastic fast food worker. Respond to the user's message.",
    response_format=ChatResponse,
)

result = agent.invoke({
    "messages": [{"role": "user", "content": "Do you have salads?"}]
})

print(result["structured_response"])
# ChatResponse(
#   message="A salad? At a burger joint? Bold move.",
#   employee_image="eyeroll.png",
#   end_conversation=False
# )
```
