# Plan: Optimize Summary Integration Tests (Options A + D)

## Goal
Reduce total API calls in `int_tests_summarize_order.py` from 17 → 6, and make each call
more deterministic by patching `temperature=0` in the test environment only.

---

## Option A — Consolidate duplicate setup

The 7 tests currently run 4 distinct conversations but assert different things about the
same output. Merge tests that share identical setup into single tests with multiple assertions.

### Consolidation map

| Before (separate tests) | After (single test) | API calls saved |
|---|---|---|
| `test_single_item_summary_called` | merged into → `test_single_item_summary` | –2 |
| `test_single_item_summary_content` | merged into → `test_single_item_summary` | |
| `test_single_item_summary_header` | merged into → `test_single_item_summary` | |
| `test_ending_comment_follows_summary` | merged into → `test_single_item_summary` | |
| `test_multi_item_summary_totals` | merged into → `test_multi_item_summary` | –6 |
| `test_multi_item_summary_all_items_present` | merged into → `test_multi_item_summary` | |
| `test_summary_includes_shiver_time` | merged into → `test_multi_item_summary` | |

### Result: 2 tests, 5 total API calls (was 7 tests, 17 calls)

| Test | `invoke()` calls |
|---|---|
| `test_single_item_summary` | 2 (order burger → "that's all") |
| `test_multi_item_summary` | 3 (order burger → order fries → "that's all") |

---

## Option D — Patch `temperature=0` for integration tests

The supervisor model is instantiated at module import time in `src/agents/supervisor.py`:

```python
model = ChatAnthropic(model="claude-sonnet-4-6", temperature=0.7, max_tokens=512)
```

Patching this in `tests/integration/conftest.py` via a session-scoped `autouse` fixture
keeps production code unchanged while ensuring all integration tests run with
`temperature=0`.

### Implementation
Add a session-scoped `autouse` fixture to `tests/integration/conftest.py`:

```python
@pytest.fixture(scope="session", autouse=True)
def deterministic_model():
    import src.agents.supervisor as sup
    sup.model.temperature = 0
```

This runs once before any integration test, sets temperature on the already-instantiated
`ChatAnthropic` object, and requires no changes to production code.

---

## Files changed
- `tests/integration/int_tests_summarize_order.py` — replace 7 tests with 2 consolidated tests
- `tests/integration/conftest.py` — add `deterministic_model` session fixture

## Files NOT changed
- `src/agents/supervisor.py` — production temperature stays at 0.7
