import uuid
import pytest
from tests.integration.conftest import invoke, get_tool_messages


@pytest.mark.integration
class TestOrderEntry:

    def test_order_valid_burger_by_alias(self, thread_id):
        result = invoke("I'd like a burger please", thread_id)
        assert result["structured_response"].intent == "order_entry"
        tool_msgs = get_tool_messages(result, "take_order")
        assert len(tool_msgs) > 0
        assert "Cheese Brrrrrrrrger" in tool_msgs[0].content
        assert "ERROR" not in tool_msgs[0].content

    def test_order_valid_fries_by_alias(self, thread_id):
        result = invoke("Can I get 2 fries", thread_id)
        assert result["structured_response"].intent == "order_entry"
        tool_msgs = get_tool_messages(result, "take_order")
        assert len(tool_msgs) > 0
        assert "Frozen Fries" in tool_msgs[0].content
        assert "2x" in tool_msgs[0].content
        assert "ERROR" not in tool_msgs[0].content

    def test_order_valid_shake_by_alias(self, thread_id):
        result = invoke("One shake please", thread_id)
        assert result["structured_response"].intent == "order_entry"
        tool_msgs = get_tool_messages(result, "take_order")
        assert len(tool_msgs) > 0
        assert "Shakes" in tool_msgs[0].content
        assert "ERROR" not in tool_msgs[0].content

    def test_order_valid_burrito_by_alias(self, thread_id):
        result = invoke("Give me a burrito", thread_id)
        assert result["structured_response"].intent == "order_entry"
        tool_msgs = get_tool_messages(result, "take_order")
        assert len(tool_msgs) > 0
        assert "Chicken Brrrrrrrrito" in tool_msgs[0].content
        assert "ERROR" not in tool_msgs[0].content

    def test_order_valid_quantity_boundary_max(self, thread_id):
        result = invoke("I want 5 burgers", thread_id)
        assert result["structured_response"].intent == "order_entry"
        tool_msgs = get_tool_messages(result, "take_order")
        assert len(tool_msgs) > 0
        assert "5x Cheese Brrrrrrrrger" in tool_msgs[0].content
        assert "ERROR" not in tool_msgs[0].content

    def test_order_invalid_quantity_over_limit(self, thread_id):
        result = invoke("I want 10 burgers", thread_id)
        tool_msgs = get_tool_messages(result, "take_order")
        assert len(tool_msgs) > 0
        assert tool_msgs[0].content.startswith("ERROR: Quantity must be between 1 and 5")

    def test_order_invalid_quantity_zero(self, thread_id):
        result = invoke("I want 0 fries", thread_id)
        assert result["structured_response"].intent == "order_entry"
        tool_msgs = get_tool_messages(result, "take_order")
        if tool_msgs:
            assert tool_msgs[0].content.startswith("ERROR:")

    def test_order_response_contains_price(self, thread_id):
        result = invoke("One frozen fries please", thread_id)
        tool_msgs = get_tool_messages(result, "take_order")
        assert len(tool_msgs) > 0
        assert "$2.95" in tool_msgs[0].content
