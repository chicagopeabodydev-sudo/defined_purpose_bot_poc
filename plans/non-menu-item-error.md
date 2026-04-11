# Plan: Add `invalid-menu-item` Error Type

## Context
Currently, ordering a real food item not on the menu (e.g., "pizza", "chicken wings") is classified as `off_topic` but falls through to the generic `simply-unrelated` error type — the same bucket used for completely unrelated topics like the weather or sports. These two cases warrant distinct responses: one acknowledges the food context but redirects to what's actually available, while the other ignores food entirely.

This plan adds a dedicated `invalid-menu-item` error type to handle the case where the user's input is food-related but names an item not found in `menu.json`.

---

## Files to Create / Update

```
src/resources/off_topic_messages.json          — add level 1 and level 2 entries for "invalid-menu-item"
src/tools/get_error_response.py                — update docstring to list new error type
src/agents/supervisor.py                       — extend off_topic classification rule in system prompt
tests/unit/tests_get_error_response.py         — add 3 new unit tests
tests/integration/int_tests_off_topic.py       — add test for invalid-menu-item intent + move existing test
tests/integration/int_tests_order_entry.py     — remove/update test that now belongs in off_topic file
```

---

## Step 1 — `off_topic_messages.json`

Add two new message entries for `errorType: "invalid-menu-item"`:

- **Level 1**: Acknowledge the item is food but isn't on the Shiver Shack menu; redirect to what is available. Sarcastic in character.
- **Level 2**: Escalate the sarcasm; reiterate the available menu items.

Example tone (final wording is up to the author):
```json
{
  "errorType": "invalid-menu-item",
  "errorLevel": 1,
  "errorMessage": "Oh sure, we definitely serve pizza here — right next to our unicorn steaks. Check the menu above, genius."
},
{
  "errorType": "invalid-menu-item",
  "errorLevel": 2,
  "errorMessage": "Still going with items we don't have? Bold strategy. Burger, burrito, fries, shake — that's the whole list. Pick one."
}
```

No logic changes to `get_error_response.py` are needed — the existing lookup and fallback already handle any new `errorType` value.

---

## Step 2 — `get_error_response.py` Docstring

Update the `error_type` docstring line to include the new value:

**Before:**
```
error_type should be one of: 'sexual-content', 'prompt-engineering', 'not-understandable', 'simply-unrelated'.
```

**After:**
```
error_type should be one of: 'sexual-content', 'prompt-engineering', 'not-understandable', 'simply-unrelated', 'invalid-menu-item'.
```

---

## Step 3 — Supervisor System Prompt (`supervisor.py`)

Extend the `off_topic` classification rule in `_SYSTEM_PROMPT` to distinguish between the two off-topic sub-cases that now require different error types:

**Before:**
```
- "off_topic": Anything unrelated to the menu or ordering food → call get_error_response.
```

**After (conceptually):**
```
- "off_topic": Anything that is not a valid order or menu question → call get_error_response with the appropriate error_type:
    - "invalid-menu-item": user named a real food item (e.g. pizza, wings, sushi) that is not in the known menu aliases list above
    - "simply-unrelated": message has no relation to food or ordering at all
    - (other existing types remain unchanged)
```

The `_build_menu_reference()` output already in the prompt provides the grounding the model needs to distinguish these two cases.

---

## Step 4 — Unit Tests (`tests_get_error_response.py`)

Add three new tests to `TestGetErrorResponse`:

| Test | What it verifies |
|---|---|
| `test_invalid_menu_item_returns_message` | Happy path — returns a message for `error_type="invalid-menu-item"` |
| `test_invalid_menu_item_level_1_returns_level_1_message` | Pool is filtered to `errorLevel == 1` |
| `test_invalid_menu_item_level_2_returns_level_2_message` | Pool is filtered to `errorLevel == 2` |

Follow the same `patch(random.choice)` pattern used by existing tests in that file.

---

## Step 5 — Integration Tests

### `int_tests_order_entry.py`
`test_order_invalid_item_not_on_menu` currently asserts `intent == "order_entry"` for `"I want a pizza please"`. This is now incorrect — pizza is off-topic under the new behavior. **Remove this test** from the order entry file.

### `int_tests_off_topic.py`
Add two new tests to `TestOffTopic`:

| Test | Input | Assert |
|---|---|---|
| `test_off_topic_invalid_menu_item_pizza` | `"I want a pizza please"` | `intent == "off_topic"`, `off_topic_count == 1`, `[OFF-TOPIC]` in last AIMessage content |
| `test_off_topic_invalid_menu_item_does_not_trigger_order` | `"Can I get some chicken wings"` | `intent == "off_topic"`, no `take_order` ToolMessage in result |

---

## Verification

After implementation, run unit tests first (no API key needed):
```
pytest -m "not integration" -v
```

Then, with approval, run integration tests:
```
pytest -m integration -v
```

All tests should pass. The previously failing `test_order_invalid_item_not_on_menu` will be gone from `int_tests_order_entry.py` and replaced by the two new off-topic tests.
