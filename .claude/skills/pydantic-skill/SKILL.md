---
name: pydantic-skill
description: Defines structured data models with Pydantic BaseModel. LangChain uses Pydantic models to define Structured Output schemas.
---

# What are Pydantic models and when to use
Pydantic models group related fields into a single component. They define **structured output**—the expected format the LLM returns.

## Pydantic models: name and collection of fields
Each field needs at minimum:
1. **Name** of the field
2. **Type** of data (e.g., `int`, `str`, `List[str]`)

## Nested models
Pydantic models can contain other models as fields:

```python
from typing import List
from pydantic import BaseModel, Field

class Song(BaseModel):
    """Data model for a song."""
    title: str
    length_seconds: int

class Album(BaseModel):
    """Data model for an album."""
    name: str
    artist: str
    songs: List[Song]
```

## Defining models for structured output (RAG / LlamaIndex)
1. **Name** the model (PascalCase)
2. **Docstring** describing what the model represents (helps the LLM)
3. **Fields** in the form `field_name: type`
4. **Optional**: `Field(..., description="...")` to guide the LLM on what to populate

```python
summary: str = Field(
    ..., description="A concise summary of this text chunk."
)
```

## Example Using Pydantic Models for Stuctured Output

```python
from pydantic import BaseModel, Field
from langchain.agents import create_agent

class ContactInfo(BaseModel):
    """Contact information for a person."""
    name: str = Field(description="The name of the person")
    email: str = Field(description="The email address of the person")
    phone: str = Field(description="The phone number of the person")

agent = create_agent(
    model="gpt-5",
    response_format=ContactInfo  # Auto-selects ProviderStrategy
)

result = agent.invoke({
    "messages": [{"role": "user", "content": "Extract contact info from: John Doe, john@example.com, (555) 123-4567"}]
})

print(result["structured_response"])
# ContactInfo(name='John Doe', email='john@example.com', phone='(555) 123-4567')
```


## Additional Resources
- [Pydantic BaseModel documentation](https://docs.pydantic.dev/latest/api/base_model/)