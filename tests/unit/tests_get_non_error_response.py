from unittest.mock import patch
import src.tools.get_non_error_response as non_error_mod
from src.tools.get_non_error_response import get_non_error_response

_PATCH_TARGET = "src.tools.get_non_error_response.random.choice"


class TestGetNonErrorResponse:

    def test_greeting_returns_message(self):
        with patch(_PATCH_TARGET, return_value={"errorMessage": "fixed"}):
            result = get_non_error_response.func(message_type="greeting")
        assert result == "fixed"

    def test_confirm_order_returns_message(self):
        with patch(_PATCH_TARGET, return_value={"errorMessage": "fixed"}):
            result = get_non_error_response.func(message_type="confirm-order")
        assert result == "fixed"

    def test_next_order_step_returns_message(self):
        with patch(_PATCH_TARGET, return_value={"errorMessage": "fixed"}):
            result = get_non_error_response.func(message_type="next-order-step")
        assert result == "fixed"

    def test_ending_session_returns_message(self):
        with patch(_PATCH_TARGET, return_value={"errorMessage": "fixed"}):
            result = get_non_error_response.func(message_type="ending-session")
        assert result == "fixed"

    def test_unknown_message_type_falls_back_to_all_messages(self):
        with patch(_PATCH_TARGET) as mock_choice:
            mock_choice.return_value = {"errorMessage": "fallback"}
            result = get_non_error_response.func(message_type="does-not-exist")
            pool = mock_choice.call_args[0][0]
        assert result == "fallback"
        assert len(pool) == 4

    def test_single_item_pools_each_have_one_item(self):
        for msg_type in ("greeting", "confirm-order", "next-order-step", "ending-session"):
            with patch(_PATCH_TARGET) as mock_choice:
                mock_choice.return_value = {"errorMessage": "x"}
                get_non_error_response.func(message_type=msg_type)
                pool = mock_choice.call_args[0][0]
            assert len(pool) == 1, f"Expected pool size 1 for '{msg_type}', got {len(pool)}"

    def test_messages_loaded_once(self, reset_non_error_cache):
        real_open = open
        call_count = {"n": 0}

        def counting_open(path, *args, **kwargs):
            if "non_error_messages.json" in str(path):
                call_count["n"] += 1
            return real_open(path, *args, **kwargs)

        with patch("builtins.open", side_effect=counting_open):
            get_non_error_response.func(message_type="greeting")
            get_non_error_response.func(message_type="greeting")

        assert call_count["n"] == 1
