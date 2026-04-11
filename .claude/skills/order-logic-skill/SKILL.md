---
name: order-logic-skill
description: Defines the components of an order, and the basic logic for the chatbot to follow when guiding users through the meal-ordering process.
---

## When to Use This Skill

Consult this skill when:
- Implementing or modifying the `take_order` tool in `src/tools/take_order.py`
- Working with order-related Pydantic models in `src/models/`
- Extending or debugging the order step flow (what happens after a user inputs an order entry)
- Adding or changing validation rules for order items or quantities
- Understanding which response type to return after parsing a user's input

## Key components
1. **Menu Item Types** — there are three order item types: main item, side, and drink
  - there are one or more menu items defined in the full menu (see below for link)
2. **Order Item** — a specific menu item and an amount
  - for example, "two cheeseburgers"
3. **Complete Meal** — one or more order items
  - cannot be empty (at least one thing ordered)
  - can contain every menu item and an amount
  - amounts greater than 5 require additional approvals
4. **Order Suggestion** — message that suggests a menu item type not already in the order
  - for example, if the order has a main item, then suggest a side
5. **Order Confirmation** — summary text of the order items along with a request for confirmation of its correctness
  - presented if the order contains at least one of each menu item type or if the user has confirmed nothing else is wanted
6. **Next Step** — defines what the supervisor should do next; maps directly to a tool call:
  - `take_order` — record the parsed item and quantity
  - `answer_menu_question` — return an answer from menu data
  - `get_error_response` — return a predefined error message (off-topic or invalid order)
  - `get_non_error_response` — return a predefined suggestion or confirmation message
  - `summarize_order` — present the final order summary
7. **Non Error Messages** — predefined messages selected by `get_non_error_response`, mapped to situations such as Order Suggestions or Order Confirmations; the LLM is **not** called to generate these
8. **Off Topic Messages** — predefined messages selected by `get_error_response`, mapped to specific off-topic scenarios; see Off-Topic Handling below

## How Order Logic Connects to the Supervisor

Every user message is first classified by the supervisor agent (`src/agents/supervisor.py`) into one of three intents via `SupervisorDecision.intent`:

| Intent | Meaning | Tool called |
|---|---|---|
| `order_entry` | User is placing or modifying an order | `take_order` |
| `menu_question` | User is asking about the menu | `answer_menu_question` |
| `off_topic` | Input unrelated to ordering | `get_error_response` |

Order logic only applies when intent is `order_entry`. The other intents bypass order logic entirely.

## Order Item Validation (Error Cases)

The `take_order` tool enforces two hard rules. Both return an error string instead of recording the item:

1. **Item not on menu** — the item name (and aliases) must match an entry in `menu.json`. If not found, an error response is returned listing available items.
2. **Quantity out of range** — quantity must be between 1 and 5 (inclusive). A quantity of 0 or greater than 5 is rejected with an error.

These errors surface back through the supervisor's response. The LLM does **not** generate error text — errors are returned directly from the tool as strings.

## Order Step Decision Tree

After `take_order` succeeds, the response type depends on the current state of the order:

```
User input classified as order_entry
    └─ take_order(item, quantity)
          ├─ ERROR: item not on menu       → get_error_response
          ├─ ERROR: quantity out of range  → get_error_response
          └─ SUCCESS: item recorded
                ├─ Order has at least one of each type (Main, Side, Drink)
                │     └─ get_non_error_response("confirm-order")
                ├─ Order is missing one or more types
                │     └─ get_non_error_response("next-order-step")  ← suggests missing type
                └─ User says nothing else is wanted
                      └─ get_non_error_response("confirm-order") → summarize_order
```

**Key rule:** Predefined responses are always selected from resource files — the LLM is never called to generate the text of a final response.

## Off-Topic Handling

When the supervisor classifies input as `off_topic`:

1. The LLM generates a response prefixed with `[OFF-TOPIC]` (enforced by the system prompt).
2. The `track_off_topic` middleware detects the prefix and increments `off_topic_count` in state.
3. `get_error_response` is called with an `error_type` and a `level`. The level is determined by how many off-topic turns have occurred in the session (counted from `[OFF-TOPIC]` markers in conversation history).
4. If `off_topic_count` reaches `OFF_TOPIC_LIMIT` (3), `track_off_topic` terminates the session and routes to `__end__`.

### Error Level Escalation

Each off-topic type (`sexual-content`, `prompt-engineering`, `not-understandable`, `simply-unrelated`) has messages at levels 1 and 2. The third off-topic message — regardless of type — uses the universal `"any"` entry at level 3:

| Session off-topic count | Level passed | Message selected from |
|---|---|---|
| 1 (first occurrence) | `level=1` | `errorType=<type>`, `errorLevel=1` |
| 2 (second occurrence) | `level=2` | `errorType=<type>`, `errorLevel=2` |
| 3+ (third or beyond) | `level=3` | `errorType="any"`, `errorLevel=3` |

The `"any"` level 3 message is a final warning delivered before `track_off_topic` ends the session. The LLM is responsible for counting prior `[OFF-TOPIC]` responses in the conversation history to determine the correct level to pass.

The logged `off_topic_count` is always the post-increment value. See [langchain-middleware-skill](../langchain-middleware-skill) for middleware implementation details.

## Additional Resources
[full menu](../../../src/resources/menu.json)
[non-error messages](../../../src/resources/non_error_messages.json)
[project goals](../project-goals-skill)
[examples](./examples.md)
