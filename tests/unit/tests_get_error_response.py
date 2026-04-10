from unittest.mock import patch
import src.tools.get_error_response as error_mod
from src.tools.get_error_response import get_error_response

_PATCH_TARGET = "src.tools.get_error_response.random.choice"


class TestGetErrorResponse:

    def test_sexual_content_returns_message(self):
        with patch(_PATCH_TARGET, return_value={"errorMessage": "fixed"}):
            result = get_error_response.func(error_type="sexual-content")
        assert result == "fixed"

    def test_prompt_engineering_returns_message(self):
        with patch(_PATCH_TARGET, return_value={"errorMessage": "fixed"}):
            result = get_error_response.func(error_type="prompt-engineering")
        assert result == "fixed"

    def test_not_understandable_returns_message(self):
        with patch(_PATCH_TARGET, return_value={"errorMessage": "fixed"}):
            result = get_error_response.func(error_type="not-understandable")
        assert result == "fixed"

    def test_simply_unrelated_returns_message(self):
        with patch(_PATCH_TARGET, return_value={"errorMessage": "fixed"}):
            result = get_error_response.func(error_type="simply-unrelated")
        assert result == "fixed"

    def test_unknown_error_type_falls_back_to_simply_unrelated(self):
        with patch(_PATCH_TARGET) as mock_choice:
            mock_choice.return_value = {"errorMessage": "fallback"}
            result = get_error_response.func(error_type="does-not-exist")
            pool = mock_choice.call_args[0][0]
        assert result == "fallback"
        assert all(m["errorType"] == "simply-unrelated" for m in pool)

    def test_empty_string_falls_back_to_simply_unrelated(self):
        with patch(_PATCH_TARGET) as mock_choice:
            mock_choice.return_value = {"errorMessage": "fallback"}
            get_error_response.func(error_type="")
            pool = mock_choice.call_args[0][0]
        assert all(m["errorType"] == "simply-unrelated" for m in pool)

    def test_sexual_content_pool_size(self):
        with patch(_PATCH_TARGET) as mock_choice:
            mock_choice.return_value = {"errorMessage": "x"}
            get_error_response.func(error_type="sexual-content")
            pool = mock_choice.call_args[0][0]
        assert len(pool) == 2

    def test_fallback_pool_size(self):
        with patch(_PATCH_TARGET) as mock_choice:
            mock_choice.return_value = {"errorMessage": "x"}
            get_error_response.func(error_type="simply-unrelated")
            pool = mock_choice.call_args[0][0]
        assert len(pool) == 3

    def test_messages_loaded_once(self, reset_error_cache):
        real_open = open
        call_count = {"n": 0}

        def counting_open(path, *args, **kwargs):
            if "off_topic_messages.json" in str(path):
                call_count["n"] += 1
            return real_open(path, *args, **kwargs)

        with patch("builtins.open", side_effect=counting_open):
            get_error_response.func(error_type="simply-unrelated")
            get_error_response.func(error_type="simply-unrelated")

        assert call_count["n"] == 1
