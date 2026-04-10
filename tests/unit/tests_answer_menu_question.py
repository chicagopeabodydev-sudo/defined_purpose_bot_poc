from unittest.mock import patch
import src.tools.answer_menu_question as answer_menu_mod
from src.tools.answer_menu_question import answer_menu_question


class TestAnswerMenuQuestion:

    def test_returns_string(self):
        result = answer_menu_question.func(question="What do you have?")
        assert isinstance(result, str)

    def test_contains_all_menu_items(self):
        result = answer_menu_question.func(question="What do you have?")
        assert "Cheese Burrrrrrrrger" in result
        assert "Chicken Burrrrrrrrito" in result
        assert "Frozen Fries" in result
        assert "Shakes" in result

    def test_contains_prices(self):
        result = answer_menu_question.func(question="How much?")
        assert "$" in result

    def test_arbitrary_question_same_output(self):
        result_a = answer_menu_question.func(question="what's hot?")
        result_b = answer_menu_question.func(question="anything else?")
        assert result_a == result_b

    def test_menu_loaded_once(self, reset_answer_menu_cache):
        real_open = open
        call_count = {"n": 0}

        def counting_open(path, *args, **kwargs):
            if "menu.json" in str(path):
                call_count["n"] += 1
            return real_open(path, *args, **kwargs)

        with patch("builtins.open", side_effect=counting_open):
            answer_menu_question.func(question="first call")
            answer_menu_question.func(question="second call")

        assert call_count["n"] == 1
