# Plan: Core Logic Implementation

## Context

A review of `src/` against the project-goals-skill and order-logic-skill revealed that several key pieces of the designed architecture were never wired together. The most critical gaps mean the predefined response system — a core architectural goal of "short-circuit LLM calls" — is completely unreachable at runtime. Additionally, the order step decision tree cannot function because ordered items are never accumulated in agent state.

---

## Issues Found

### Critical — Core functionality is broken

**Issue 1: `get_non_error_response` and summarize tools are not registered with the supervisor**

`src/agents/supervisor.py` registers only:
```python
tools=[take_order, answer_menu_question, get_error_response]
```
`get_non_error_response`, `summarize_order_entry`, and `summarize_complete_order` are absent. The LLM has no knowledge of them and can never call them.

**Impact:** Order confirmations, next-step suggestions, and order summaries are all unreachable. The predefined response design goal cannot be achieved.

**Issue 2: `OrderState` does not accumulate order items**

`OrderState` in `src/middleware/off_topic_tracker.py` only tracks `off_topic_count`. There is no field for the running list of ordered items. Without structured order state the supervisor cannot:
- Know whether Main, Side, and Drink item types are all covered
- Decide between calling `confirm-order` vs `next-order-step`
- Pass a complete item list to `summarize_complete_order`

**Impact:** The order step decision tree from the order-logic-skill cannot be executed as designed.

---

### Moderate — Design goals violated

**Issue 3: Greeting is hardcoded in `main.py`**

`src/main.py` defines `GREETING` as a hardcoded string constant. The `greeting` message type exists in `non_error_messages.json` and should be retrieved via `get_non_error_response("greeting")` to keep all copy centralized in the resource system.

**Issue 4: `ChatResponse` model is defined but never used**

`src/models/chat_response.py` defines a model with `message`, `employee_image`, and `end_conversation` fields, but nothing in the codebase imports or uses it. All responses are delivered as plain strings via `SupervisorDecision.response`. This is dead code.

---

## Proposed Fixes

### Fix 1 — Register missing tools with the supervisor
**File:** `src/agents/supervisor.py`

Add `get_non_error_response`, `summarize_order_entry`, and `summarize_complete_order` to the `tools` list. Update `_SYSTEM_PROMPT` to instruct the LLM when to call each:
- `get_non_error_response("next-order-step")` — item recorded, not all three item types present yet
- `get_non_error_response("confirm-order")` — all three types present, or user says no more items
- `summarize_complete_order(items, total_price, minutes_to_shiver)` — user confirms the order is complete

### Fix 2 — Add `order_items` to `OrderState` and accumulate via middleware
**File:** `src/middleware/off_topic_tracker.py`

Add `order_items: NotRequired[list[dict]]` to `OrderState`.

Add a new `after_model` middleware function `track_order` that inspects the most recent tool result messages in agent state: when a `take_order` call succeeded (result does not start with `"ERROR:"`), extract the item and quantity and append to `state["order_items"]`.

Register `track_order` in the supervisor's middleware list (before `track_off_topic`).

### Fix 3 — Load greeting from resource file
**File:** `src/main.py`

Replace the hardcoded `GREETING` constant with a lookup from `non_error_messages.json` for the `greeting` message type, keeping all copy in the resource system.

### Fix 4 — Remove unused `ChatResponse` model
**Files:** `src/models/chat_response.py`, `src/models/__init__.py`

Delete `chat_response.py`. Remove any `ChatResponse` import from `__init__.py` if present. Nothing in the codebase imports it.

---

## Files to Modify

| File | Change |
|---|---|
| `src/agents/supervisor.py` | Add 3 missing tools; update system prompt |
| `src/middleware/off_topic_tracker.py` | Add `order_items` to `OrderState`; add `track_order` middleware |
| `src/main.py` | Replace hardcoded greeting with resource lookup |
| `src/models/chat_response.py` | Delete (dead code) |
| `src/models/__init__.py` | Remove `ChatResponse` import if present |

---

## Verification

1. Run existing unit tests — `pytest tests/unit/` — to confirm no regressions.
2. Manual REPL test: place a complete order (main + side + drink) and verify:
   - Each successful `take_order` call triggers `get_non_error_response` (not a raw LLM string)
   - After all three item types are present, `confirm-order` fires
   - After user confirms, `summarize_complete_order` fires with correct items, total price, and shiver time
3. Manual REPL test: send 3 off-topic messages and confirm session terminates correctly.
4. Confirm greeting at startup matches the value in `non_error_messages.json`.
