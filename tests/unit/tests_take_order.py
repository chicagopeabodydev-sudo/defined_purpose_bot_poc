from unittest.mock import patch, mock_open
import src.tools.take_order as take_order_mod
from src.tools.take_order import take_order


class TestTakeOrder:

    def test_valid_order_by_primary_name(self):
        result = take_order.func(item="Frozen Fries", quantity=1)
        assert "Frozen Fries" in result
        assert "ERROR" not in result

    def test_valid_order_by_alias_burger(self):
        result = take_order.func(item="burger", quantity=1)
        assert "Cheese Brrrrrrrrger" in result
        assert "ERROR" not in result

    def test_valid_order_by_alias_burrito(self):
        result = take_order.func(item="burrito", quantity=1)
        assert "Chicken Brrrrrrrrito" in result
        assert "ERROR" not in result

    def test_valid_order_by_alias_fries(self):
        result = take_order.func(item="fries", quantity=1)
        assert "Frozen Fries" in result
        assert "ERROR" not in result

    def test_valid_order_by_alias_shake(self):
        result = take_order.func(item="shake", quantity=1)
        assert "Shakes" in result
        assert "ERROR" not in result

    def test_case_insensitive_item_name_upper(self):
        result = take_order.func(item="BURGER", quantity=1)
        assert "ERROR" not in result

    def test_case_insensitive_item_name_mixed(self):
        result = take_order.func(item="Burger", quantity=1)
        assert "ERROR" not in result

    def test_quantity_minimum_boundary(self):
        result = take_order.func(item="Frozen Fries", quantity=1)
        assert "ERROR" not in result

    def test_quantity_maximum_boundary(self):
        result = take_order.func(item="Frozen Fries", quantity=5)
        assert "ERROR" not in result

    def test_quantity_zero_invalid(self):
        result = take_order.func(item="Frozen Fries", quantity=0)
        assert "ERROR" in result

    def test_quantity_six_invalid(self):
        result = take_order.func(item="Frozen Fries", quantity=6)
        assert "ERROR" in result

    def test_quantity_negative_invalid(self):
        result = take_order.func(item="Frozen Fries", quantity=-1)
        assert "ERROR" in result

    def test_item_not_found(self):
        result = take_order.func(item="Spaghetti Bolognese", quantity=1)
        assert "ERROR" in result
        assert "Spaghetti Bolognese" in result

    def test_partial_name_no_match(self):
        result = take_order.func(item="burg", quantity=1)
        assert "ERROR" in result

    def test_menu_loaded_once(self, reset_take_order_cache):
        real_open = open
        call_count = {"n": 0}

        def counting_open(path, *args, **kwargs):
            if "menu.json" in str(path):
                call_count["n"] += 1
            return real_open(path, *args, **kwargs)

        with patch("builtins.open", side_effect=counting_open):
            take_order.func(item="fries", quantity=1)
            take_order.func(item="fries", quantity=2)

        assert call_count["n"] == 1
