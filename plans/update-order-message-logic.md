# Plan: Update Logic for New non_error_messages.json Format

## Context

`src/resources/non_error_messages.json` was restructured. The old format had 4 message types (`greeting`, `confirm-order`, `next-order-step`, `ending-session`). The new format introduces 5 more granular types with a `message` field (not `errorMessage`):

| New messageType | Count | When used |
|---|---|---|
| `greeting` | 2 | Start of conversation |
| `next-step-only-main-ordered` | 2 | Only a Main item in the order |
| `next-step-main-and-side-ordered` | 1 | Main + Side in the order, no Drink |
| `next-step-generic` | 2 | Any other successful order state |
| `ending-comment` | 2 | After final order summary |

New conversation flow:
1. `greeting` → conversation start
2. After each successful `take_order` → appropriate `next-step-*` based on what's in the order
3. User says done → `summarize_complete_order` THEN `ending-comment`

Two pre-existing bugs are also being fixed as part of this work: both `get_non_error_response.py` and `main.py` access `["errorMessage"]` on non-error messages — this is a KeyError at runtime since the correct key is `"message"`.

---

## Changes

### 1. `src/tools/get_non_error_response.py`

**a)** Fix key access on line 30:
- `["errorMessage"]` → `["message"]`

**b)** Update docstring (line 23) to list new message types:
```
message_type should be one of: 'greeting', 'next-step-only-main-ordered',
'next-step-main-and-side-ordered', 'next-step-generic', 'ending-comment'.
```

---

### 2. `src/main.py`

**a)** Add `import random` to stdlib imports.

**b)** Fix `_get_greeting()` return statement:
- `matches[0]["errorMessage"]` → `random.choice(matches)["message"]`
  (also enables random greeting selection from the 2 available entries)

---

### 3. `src/agents/supervisor.py`

Replace the `order_entry` block in `_SYSTEM_PROMPT` with the new three-branch `next-step-*` logic and corrected ending flow:

**Old:**
```
- "order_entry": User is trying to order food → call take_order, then:
    - If take_order returns an ERROR, call get_error_response with error_type "not-understandable"
    - If take_order succeeds AND the order now contains at least one Main, one Side, AND one Drink,
      call get_non_error_response with message_type "confirm-order"
    - If take_order succeeds AND the order is still missing one or more item types,
      call get_non_error_response with message_type "next-order-step"
    - If the user says they want nothing else (e.g. "that's all", "I'm done"),
      call get_non_error_response with message_type "confirm-order", then call summarize_complete_order
```

**New:**
```
- "order_entry": User is trying to order food → call take_order, then:
    - If take_order returns an ERROR, call get_error_response with error_type "not-understandable"
    - If take_order succeeds AND the order has ONLY a Main (no Side, no Drink),
      call get_non_error_response with message_type "next-step-only-main-ordered"
    - If take_order succeeds AND the order has a Main AND a Side (no Drink),
      call get_non_error_response with message_type "next-step-main-and-side-ordered"
    - If take_order succeeds AND the order has any other combination (all three, or only Side/Drink),
      call get_non_error_response with message_type "next-step-generic"
    - If the user says they want nothing else (e.g. "that's all", "I'm done"),
      call summarize_complete_order THEN call get_non_error_response with message_type "ending-comment"
```

---

### 4. `tests/unit/tests_get_non_error_response.py`

All tests are broken due to two root causes:

**Root cause A — wrong key in all mocked return values (every test)**
All mock patches return `{"errorMessage": "fixed"}` but the tool now reads `["message"]`. Fix: change every mock `return_value` to `{"message": "fixed"}`.

**Root cause B — stale message type strings**

| Test | Old type | New type |
|---|---|---|
| `test_confirm_order_returns_message` (line 15) | `"confirm-order"` | `"next-step-only-main-ordered"` |
| `test_next_order_step_returns_message` (line 20) | `"next-order-step"` | `"next-step-main-and-side-ordered"` |
| `test_ending_session_returns_message` (line 25) | `"ending-session"` | `"ending-comment"` |
| `test_unknown_message_type_falls_back_to_all_messages` (line 30) | pool size assert `== 4` | change to `== 9` (new JSON has 9 total entries) |
| `test_single_item_pools_each_have_one_item` (line 38) | iterates 4 old types, asserts pool size 1 each | rewrite to assert correct pool sizes: greeting=2, next-step-only-main-ordered=2, next-step-main-and-side-ordered=1, next-step-generic=2, ending-comment=2 |

`test_messages_loaded_once` (line 46) is unaffected — no changes needed.

---

### 5. `.claude/skills/order-logic-skill/SKILL.md`

Update the **Order Step Decision Tree** section:

**Old:**
```
├─ Order has at least one of each type (Main, Side, Drink)
│     └─ get_non_error_response("confirm-order")
├─ Order is missing one or more types
│     └─ get_non_error_response("next-order-step")  ← suggests missing type
└─ User says nothing else is wanted
      └─ get_non_error_response("confirm-order") → summarize_order
```

**New:**
```
├─ Order has ONLY a Main (no Side, no Drink)
│     └─ get_non_error_response("next-step-only-main-ordered")
├─ Order has a Main AND a Side (no Drink)
│     └─ get_non_error_response("next-step-main-and-side-ordered")
├─ Any other successful combination
│     └─ get_non_error_response("next-step-generic")
└─ User says nothing else is wanted
      └─ summarize_complete_order → get_non_error_response("ending-comment")
```

---

### 6. `.claude/skills/order-logic-skill/examples.md`

Update the **Happy Path** table (lines 9–12):

| Turn | User Input | Intent | Tool Called | Response Type |
|---|---|---|---|---|
| 1 | "I'd like a cheeseburger" | `order_entry` | `take_order(...)` | `get_non_error_response("next-step-only-main-ordered")` |
| 2 | "and some fries" | `order_entry` | `take_order(...)` | `get_non_error_response("next-step-main-and-side-ordered")` |
| 3 | "and a shake" | `order_entry` | `take_order(...)` | `get_non_error_response("next-step-generic")` |
| 4 | "that's all" | `order_entry` | `summarize_complete_order` then `get_non_error_response("ending-comment")` | final summary + ending message |

Update error path tables (lines 23, 34): `"next-order-step"` → `"next-step-generic"`.

---

## Implementation Order

1. `src/tools/get_non_error_response.py` — fix the tool first (everything depends on it)
2. `src/main.py` — fix greeting loader
3. `tests/unit/tests_get_non_error_response.py` — update tests; run `pytest tests/unit/tests_get_non_error_response.py` to confirm all pass
4. `src/agents/supervisor.py` — update system prompt
5. `.claude/skills/order-logic-skill/SKILL.md` and `examples.md` — documentation last

---

## Verification

1. Run `pytest tests/unit/tests_get_non_error_response.py` — all 6 tests should pass
2. Run `pytest tests/unit/` — no regressions in other tests
3. Manual smoke test via `src/main.py` REPL:
   - Greeting displays (no KeyError)
   - Order a main → response suggests a side or drink
   - Add a side → response suggests a drink
   - Add a drink → generic "anything else?" response
   - Say "that's all" → order summary displays, followed by an ending comment

---

## Note

The `non-error-response-type` enum table in `.claude/skills/project-overview-skill/SKILL.md` also lists the old type values and is now stale. Not in scope for this change but worth a follow-up update for consistency.
