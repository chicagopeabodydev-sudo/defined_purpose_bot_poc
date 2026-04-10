import pytest
from pydantic import ValidationError
from src.tools.summarize_order import summarize_order_entry, summarize_complete_order


class TestSummarizeOrderEntry:

    def test_single_item_format(self):
        result = summarize_order_entry.func(item="Frozen Fries", quantity=1)
        assert result == "1x Frozen Fries"

    def test_multiple_quantity_format(self):
        result = summarize_order_entry.func(item="Shakes", quantity=3)
        assert result == "3x Shakes"

    def test_returns_string(self):
        result = summarize_order_entry.func(item="Shakes", quantity=2)
        assert isinstance(result, str)

    def test_no_exception_on_valid_input(self):
        summarize_order_entry.func(item="Cheese Burrrrrrrrger", quantity=5)


class TestSummarizeCompleteOrder:

    def test_single_item_order_summary(self):
        result = summarize_complete_order.func(
            items=[{"item": "Frozen Fries", "quantity": 2}],
            total_price=5.90,
            minutes_to_shiver=16,
        )
        assert "Frozen Fries" in result
        assert "5.90" in result
        assert "16" in result

    def test_multiple_items_summary(self):
        result = summarize_complete_order.func(
            items=[
                {"item": "Cheese Burrrrrrrrger", "quantity": 1},
                {"item": "Shakes", "quantity": 2},
            ],
            total_price=12.85,
            minutes_to_shiver=36,
        )
        assert "Cheese Burrrrrrrrger" in result
        assert "Shakes" in result

    def test_total_price_in_output(self):
        result = summarize_complete_order.func(
            items=[{"item": "Frozen Fries", "quantity": 1}],
            total_price=9.99,
            minutes_to_shiver=8,
        )
        assert "9.99" in result

    def test_minutes_to_shiver_in_output(self):
        result = summarize_complete_order.func(
            items=[{"item": "Frozen Fries", "quantity": 1}],
            total_price=2.95,
            minutes_to_shiver=15,
        )
        assert "15" in result

    def test_returns_string(self):
        result = summarize_complete_order.func(
            items=[{"item": "Frozen Fries", "quantity": 1}],
            total_price=2.95,
            minutes_to_shiver=8,
        )
        assert isinstance(result, str)

    def test_zero_price_edge_case(self):
        result = summarize_complete_order.func(
            items=[{"item": "Frozen Fries", "quantity": 1}],
            total_price=0.0,
            minutes_to_shiver=0,
        )
        assert "0.00" in result
