import pytest
from tests.integration.conftest import invoke, get_tool_messages


@pytest.mark.integration
class TestSummarizeOrder:

    def test_single_item_summary(self, thread_id):
        # Cheese Brrrrrrrrger: $5.95, 12 min to shiver
        invoke("I'd like a burger please", thread_id)
        result = invoke("that's all", thread_id)
        summary_msgs = get_tool_messages(result, "summarize_complete_order")
        ending_msgs = get_tool_messages(result, "get_non_error_response")

        assert len(summary_msgs) > 0, "summarize_complete_order was not called"
        summary = summary_msgs[0].content
        assert "Shiver Shack Order" in summary
        assert "Cheese Brrrrrrrrger" in summary
        assert "5.95" in summary
        assert len(ending_msgs) > 0, "get_non_error_response (ending-comment) was not called"

    def test_multi_item_summary(self, thread_id):
        # Cheese Brrrrrrrrger $5.95 + Frozen Fries $2.95 = $8.90, 12+8=20 min to shiver
        invoke("I'd like a burger please", thread_id)
        invoke("and an order of fries", thread_id)
        result = invoke("that's all", thread_id)
        summary_msgs = get_tool_messages(result, "summarize_complete_order")

        assert len(summary_msgs) > 0, "summarize_complete_order was not called"
        summary = summary_msgs[0].content
        assert "Cheese Brrrrrrrrger" in summary
        assert "Frozen Fries" in summary
        assert "8.90" in summary
        assert "20" in summary
