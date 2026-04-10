# Plan: Unit Tests for src/ Functions

## Context
The project has no tests yet. CLAUDE.md requires unit tests covering valid/invalid input, success/error paths, and common/uncommon scenarios. This plan covers tools and models only — middleware and the supervisor agent involve the LangGraph runtime and belong in integration tests.

---

## Files to Create

```
./pytest.ini                          — pytest discovery config
./tests/__init__.py                   — empty
./tests/unit/__init__.py              — empty
./tests/unit/conftest.py              — shared cache-reset fixtures
./tests/unit/tests_take_order.py      — ~14 tests
./tests/unit/tests_answer_menu_question.py  — ~5 tests
./tests/unit/tests_get_error_response.py    — ~9 tests
./tests/unit/tests_get_non_error_response.py — ~7 tests
./tests/unit/tests_summarize_order.py — ~10 tests
./tests/unit/tests_models.py          — ~11 tests
```

---

## pytest.ini

```ini
[pytest]
testpaths = tests
python_files = tests_*.py
python_classes = Test*
python_functions = test_*
```

---

## conftest.py

Fixtures using `importlib.reload(module)` to reset module-level globals (`_menu`, `_error_messages`, `_non_error_messages`) between tests. One fixture per tool module, `autouse=False` (applied selectively to cache tests).

---

## Test Files

### tests_take_order.py — `TestTakeOrder`
Calls `take_order.func(item, quantity)`.

| Test | Coverage |
|---|---|
| `test_valid_order_by_primary_name` | Happy path, primary name match |
| `test_valid_order_by_alias_burger` | Alias → canonical name |
| `test_valid_order_by_alias_burrito` | Alias lookup |
| `test_valid_order_by_alias_fries` | Alias lookup |
| `test_valid_order_by_alias_shake` | Alias lookup |
| `test_case_insensitive_item_name` | "BURGER" and "Burger" both resolve |
| `test_quantity_minimum_boundary` | qty=1 valid |
| `test_quantity_maximum_boundary` | qty=5 valid |
| `test_quantity_zero_invalid` | qty=0 returns error |
| `test_quantity_six_invalid` | qty=6 returns error |
| `test_quantity_negative_invalid` | qty=-1 returns error |
| `test_item_not_found` | Unknown item returns error |
| `test_partial_name_no_match` | "burg" (partial) returns error |
| `test_menu_loaded_once` | `open` called once across two calls (patch + call_count) |

### tests_answer_menu_question.py — `TestAnswerMenuQuestion`
Calls `answer_menu_question.func(question)`.

| Test | Coverage |
|---|---|
| `test_returns_string` | Return type |
| `test_contains_all_menu_items` | All 4 item names in output |
| `test_contains_prices` | Price values present |
| `test_arbitrary_question_same_output` | Question param ignored |
| `test_menu_loaded_once` | Caching: open called once |

### tests_get_error_response.py — `TestGetErrorResponse`
Calls `get_error_response.func(error_type)`. Mocks `src.tools.get_error_response.random.choice`.

| Test | Coverage |
|---|---|
| `test_sexual_content_returns_message` | Known type returns message |
| `test_prompt_engineering_returns_message` | Known type |
| `test_not_understandable_returns_message` | Known type |
| `test_simply_unrelated_returns_message` | Known type |
| `test_unknown_error_type_falls_back` | Unknown type → simply-unrelated |
| `test_empty_string_falls_back` | Empty string → fallback |
| `test_sexual_content_pool_size` | `random.choice` receives 2-item list |
| `test_fallback_pool_size` | `random.choice` receives 3-item list |
| `test_messages_loaded_once` | Caching: open called once |

### tests_get_non_error_response.py — `TestGetNonErrorResponse`
Calls `get_non_error_response.func(message_type)`. Mocks `random.choice`.

| Test | Coverage |
|---|---|
| `test_greeting_returns_message` | Known type |
| `test_confirm_order_returns_message` | Known type |
| `test_next_order_step_returns_message` | Known type |
| `test_ending_session_returns_message` | Known type |
| `test_unknown_message_type_falls_back` | Unknown type → full pool fallback |
| `test_single_item_pools_each_have_one_item` | Each known type has 1 message in pool |
| `test_messages_loaded_once` | Caching: open called once |

### tests_summarize_order.py — `TestSummarizeOrderEntry` + `TestSummarizeCompleteOrder`
Calls `.func()` on both tools.

| Test | Coverage |
|---|---|
| `test_single_item_format` | qty=1 → "1x Frozen Fries" |
| `test_multiple_quantity_format` | qty=3 format |
| `test_entry_returns_string` | Return type |
| `test_entry_no_exception_on_valid_input` | No ValidationError raised |
| `test_single_item_order_summary` | Item, price, minutes all in output |
| `test_multiple_items_summary` | Two item names both in output |
| `test_total_price_in_output` | Price formatted in string |
| `test_minutes_to_shiver_in_output` | minutes_to_shiver appears |
| `test_complete_returns_string` | Return type |
| `test_zero_price_edge_case` | total_price=0.0 no exception |

### tests_models.py — `TestOrderEntry`, `TestCompleteOrder`, `TestChatResponse`

| Test | Coverage |
|---|---|
| `test_order_entry_valid` | Valid construction, fields accessible |
| `test_order_entry_item_type` | item is str |
| `test_order_entry_quantity_type` | quantity is int |
| `test_order_entry_missing_item_raises` | ValidationError |
| `test_order_entry_missing_quantity_raises` | ValidationError |
| `test_complete_order_valid` | All fields provided |
| `test_complete_order_empty_items` | items=[] accepted |
| `test_complete_order_missing_field_raises` | ValidationError |
| `test_chat_response_valid_with_image` | All fields |
| `test_chat_response_optional_image` | employee_image=None |
| `test_chat_response_missing_message_raises` | ValidationError |

---

## Key Implementation Notes

**Accessing tool functions**: Use `.func` attribute — e.g., `take_order.func(item, quantity)`. This bypasses the LangChain `@tool` wrapper. Verify attribute name is correct for the installed LangChain version before writing tests.

**Cache isolation**: Use `importlib.reload(module)` in fixtures rather than patching private variables — more resilient to variable renames. Apply via `autouse=True` on all tool test classes, or selectively for the cache tests only.

**Mocking random**: Always patch at the module level where `random` is imported:
```python
patch("src.tools.get_error_response.random.choice", return_value="fixed message")
```

**Real JSON fixtures**: Use the actual resource files in `src/resources/` — they are static and tests catching JSON schema regressions is a feature.

---

## Verification

After implementation, run:
```
pytest tests/unit/ -v
```
All ~56 tests should pass. Re-run after any change to `src/tools/` or `src/models/`.
