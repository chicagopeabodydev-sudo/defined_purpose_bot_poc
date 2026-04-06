---
name: pydantic-skill
description: Defines structured data models with Pydantic BaseModel. LangChain uses Pydantic models to define Structured Output schemas.
---

# What are Pydantic Models and When to Use Them

Pydantic models group related fields into a single typed component. In this project they serve two core purposes:

1. **Parsing user input** — extracting structured data from natural language (e.g., a menu item and quantity from `"I'll take 2 burgers please"`)
2. **Defining structured output** — specifying the exact format the LLM must return so downstream code can rely on it

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

## Defining Models for Structured Output
1. **Name** the model (PascalCase)
2. **Docstring** describing what the model represents (helps the LLM)
3. **Fields** in the form `field_name: type`
4. **Optional**: `Field(..., description="...")` to guide the LLM on what to populate

```python
summary: str = Field(
    ..., description="A concise summary of this text chunk."
)
```

## Additional Resources
- For usage examples, see [examples.md](examples.md)
- [Pydantic Models guide](https://docs.pydantic.dev/latest/concepts/models/)
- [Pydantic Fields guide](https://docs.pydantic.dev/latest/concepts/fields/)
- [Pydantic BaseModel API reference](https://docs.pydantic.dev/latest/api/base_model/)