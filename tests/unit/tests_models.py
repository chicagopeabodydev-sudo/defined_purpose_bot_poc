import pytest
from pydantic import ValidationError
from src.models.order_entry import OrderEntry
from src.models.complete_order import CompleteOrder
from src.models.chat_response import ChatResponse


class TestOrderEntry:

    def test_valid_construction(self):
        entry = OrderEntry(item="Frozen Fries", quantity=2)
        assert entry.item == "Frozen Fries"
        assert entry.quantity == 2

    def test_item_is_string(self):
        entry = OrderEntry(item="Shakes", quantity=1)
        assert isinstance(entry.item, str)

    def test_quantity_is_int(self):
        entry = OrderEntry(item="Shakes", quantity=1)
        assert isinstance(entry.quantity, int)

    def test_missing_item_raises(self):
        with pytest.raises(ValidationError):
            OrderEntry(quantity=1)

    def test_missing_quantity_raises(self):
        with pytest.raises(ValidationError):
            OrderEntry(item="Shakes")


class TestCompleteOrder:

    def test_valid_construction(self):
        entries = [OrderEntry(item="Frozen Fries", quantity=1)]
        order = CompleteOrder(items=entries, total_price=2.95, minutes_to_shiver=8)
        assert order.total_price == 2.95
        assert order.minutes_to_shiver == 8

    def test_items_is_list(self):
        entries = [OrderEntry(item="Frozen Fries", quantity=1)]
        order = CompleteOrder(items=entries, total_price=2.95, minutes_to_shiver=8)
        assert isinstance(order.items, list)

    def test_empty_items_list_accepted(self):
        order = CompleteOrder(items=[], total_price=0.0, minutes_to_shiver=0)
        assert order.items == []

    def test_missing_field_raises(self):
        entries = [OrderEntry(item="Frozen Fries", quantity=1)]
        with pytest.raises(ValidationError):
            CompleteOrder(items=entries, minutes_to_shiver=8)


class TestChatResponse:

    def test_valid_with_image(self):
        resp = ChatResponse(message="Hello", employee_image="img.png", end_conversation=False)
        assert resp.message == "Hello"
        assert resp.employee_image == "img.png"
        assert resp.end_conversation is False

    def test_valid_without_image(self):
        resp = ChatResponse(message="Hello")
        assert resp.employee_image is None

    def test_end_conversation_defaults_to_false(self):
        resp = ChatResponse(message="Hello")
        assert resp.end_conversation is False

    def test_end_conversation_true(self):
        resp = ChatResponse(message="Goodbye", end_conversation=True)
        assert resp.end_conversation is True

    def test_missing_message_raises(self):
        with pytest.raises(ValidationError):
            ChatResponse(end_conversation=False)
