# Plan: Fix `summarize_complete_order` Tool Schema

## Problem
`summarize_complete_order` is defined with `items: list[dict]` as its parameter type.
When LangChain generates the JSON Schema for this tool it produces:

```json
{ "type": "array", "items": { "type": "object" } }
```

An `object` with no `properties` defined fails Anthropic's strict tool schema
validation, causing a `500 InternalServerError` before the model even runs.

All other tools use simple scalar types (`str`, `int`) that pass strict validation.

## Fix
Replace `items: list[dict]` with `items: list[OrderEntry]`.

`OrderEntry` is a Pydantic `BaseModel` with typed fields (`item: str`,
`quantity: int`). LangChain will expand it into a fully-specified JSON Schema:

```json
{
  "type": "array",
  "items": {
    "type": "object",
    "properties": {
      "item":     { "type": "string" },
      "quantity": { "type": "integer" }
    },
    "required": ["item", "quantity"]
  }
}
```

This satisfies strict validation and removes the need for the manual
`[OrderEntry(**i) for i in items]` conversion inside the function body,
since LangChain will deserialize each dict into an `OrderEntry` automatically.

## File changed
`src/tools/summarize_order.py` — one signature change + remove the manual
deserialization line.

### Before
```python
@tool
def summarize_complete_order(items: list[dict]) -> str:
    """Format the complete order with all items, total price, and shiver time.

    items should be a list of dicts with 'item' and 'quantity' keys.
    Prices and shiver times are looked up from the menu automatically.
    """
    order_entries = [OrderEntry(**i) for i in items]
    ...
```

### After
```python
@tool
def summarize_complete_order(items: list[OrderEntry]) -> str:
    """Format the complete order with all items, total price, and shiver time.

    Prices and shiver times are looked up from the menu automatically.
    """
    order_entries = items
    ...
```

## Files NOT changed
- `src/models/order_entry.py` — no changes needed
- `src/agents/supervisor.py` — tool registration unchanged
- All test files — existing assertions remain valid

## How to verify
1. Run unit tests — `tests/unit/tests_summarize_order.py` should still pass
   (the `.func()` call interface is unchanged)
2. Run the summarize order integration test — the 500 error should be gone
