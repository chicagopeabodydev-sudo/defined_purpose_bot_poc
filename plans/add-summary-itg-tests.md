# Plan: Integration Tests for `summarize_complete_order`

## Goal
Add end-to-end integration tests that verify the `summarize_complete_order` tool is called correctly by the supervisor after a user completes an order, and that the summary output is accurate.

## File
`tests/integration/int_tests_summarize_order.py`

## Approach
Follow the same pattern as existing integration tests (`int_tests_order_entry.py`):
- Use `invoke()` and `get_tool_messages()` from `conftest.py`
- Each test uses a fresh `thread_id` fixture for isolation
- Multi-step tests make sequential `invoke()` calls on the same thread to build conversation state before triggering the summary

## Test Scenarios

| Test | Input flow | Assertion |
|---|---|---|
| `test_single_item_summary_called` | Order burger → "that's all" | `summarize_complete_order` tool message exists |
| `test_single_item_summary_content` | Order burger → "that's all" | Summary contains item name and `$5.95` |
| `test_single_item_summary_header` | Order burger → "that's all" | Summary contains `Shiver Shack Order` header |
| `test_multi_item_summary_totals` | Order burger → order fries → "that's all" | Summary contains `$8.90` (5.95 + 2.95) |
| `test_multi_item_summary_all_items_present` | Order burger → order fries → "that's all" | Both item names appear in summary |
| `test_summary_includes_shiver_time` | Order burger → order fries → "that's all" | Shiver time `20` appears (burger=12, fries=8) |
| `test_ending_comment_follows_summary` | Order burger → "that's all" | `get_non_error_response` tool also called with `ending-comment` |

## Menu values used (from menu.json)
- `Cheese Brrrrrrrrger`: $5.95, 12 min to shiver
- `Frozen Fries`: $2.95, 8 min to shiver
- Combined total: $8.90, 20 min to shiver

## Notes
- Tests are marked `@pytest.mark.integration` to match existing convention
- Requires `ANTHROPIC_API_KEY` to be set (enforced by `conftest.py`)
- Must receive approval before running integration tests
