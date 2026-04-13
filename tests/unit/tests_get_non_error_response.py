from unittest.mock import patch
import src.tools.get_non_error_response as non_error_mod
from src.tools.get_non_error_response import get_non_error_response

_PATCH_TARGET = "src.tools.get_non_error_response.random.choice"


class TestGetNonErrorResponse:

    def test_greeting_returns_message(self):
        with patch(_PATCH_TARGET, return_value={"message": "fixed"}):
            result = get_non_error_response.func(message_type="greeting")
        assert result == "fixed"

    def test_next_step_only_main_ordered_returns_message(self):
        with patch(_PATCH_TARGET, return_value={"message": "fixed"}):
            result = get_non_error_response.func(message_type="next-step-only-main-ordered")
        assert result == "fixed"

    def test_next_step_main_and_side_ordered_returns_message(self):
        with patch(_PATCH_TARGET, return_value={"message": "fixed"}):
            result = get_non_error_response.func(message_type="next-step-main-and-side-ordered")
        assert result == "fixed"

    def test_ending_comment_returns_message(self):
        with patch(_PATCH_TARGET, return_value={"message": "fixed"}):
            result = get_non_error_response.func(message_type="ending-comment")
        assert result == "fixed"

    def test_unknown_message_type_falls_back_to_all_messages(self):
        with patch(_PATCH_TARGET) as mock_choice:
            mock_choice.return_value = {"message": "fallback"}
            result = get_non_error_response.func(message_type="does-not-exist")
            pool = mock_choice.call_args[0][0]
        assert result == "fallback"
        assert len(pool) == 9

    def test_pool_sizes_match_json_counts(self):
        expected_pool_sizes = {
            "greeting": 2,
            "next-step-only-main-ordered": 2,
            "next-step-main-and-side-ordered": 1,
            "next-step-generic": 2,
            "ending-comment": 2,
        }
        for msg_type, expected_size in expected_pool_sizes.items():
            with patch(_PATCH_TARGET) as mock_choice:
                mock_choice.return_value = {"message": "x"}
                get_non_error_response.func(message_type=msg_type)
                pool = mock_choice.call_args[0][0]
            assert len(pool) == expected_size, f"Expected pool size {expected_size} for '{msg_type}', got {len(pool)}"

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
