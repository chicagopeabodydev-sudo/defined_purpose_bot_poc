import pytest
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
        summarize_order_entry.func(item="Cheese Brrrrrrrrger", quantity=5)


class TestSummarizeCompleteOrder:

    def test_single_item_computes_price(self):
        # Frozen Fries: $2.95 × 2 = $5.90
        result = summarize_complete_order.func(
            items=[{"item": "Frozen Fries", "quantity": 2}]
        )
        assert "Frozen Fries" in result
        assert "5.90" in result

    def test_single_item_computes_shiver_time(self):
        # Frozen Fries: 8 min to shiver
        result = summarize_complete_order.func(
            items=[{"item": "Frozen Fries", "quantity": 1}]
        )
        assert "8" in result

    def test_multiple_items_total_price(self):
        # Cheese Brrrrrrrrger $5.95 + Frozen Fries $2.95 = $8.90
        result = summarize_complete_order.func(
            items=[
                {"item": "Cheese Brrrrrrrrger", "quantity": 1},
                {"item": "Frozen Fries", "quantity": 1},
            ]
        )
        assert "8.90" in result

    def test_multiple_items_summary(self):
        result = summarize_complete_order.func(
            items=[
                {"item": "Cheese Brrrrrrrrger", "quantity": 1},
                {"item": "Shakes", "quantity": 1},
            ]
        )
        assert "Cheese Brrrrrrrrger" in result
        assert "Shakes" in result

    def test_returns_string(self):
        result = summarize_complete_order.func(
            items=[{"item": "Frozen Fries", "quantity": 1}]
        )
        assert isinstance(result, str)

    def test_contains_order_header(self):
        result = summarize_complete_order.func(
            items=[{"item": "Frozen Fries", "quantity": 1}]
        )
        assert "Shiver Shack Order" in result

    def test_unknown_item_graceful(self):
        # Unknown items should not crash; totals default to 0
        result = summarize_complete_order.func(
            items=[{"item": "Mystery Item", "quantity": 1}]
        )
        assert "0.00" in result
        assert isinstance(result, str)
