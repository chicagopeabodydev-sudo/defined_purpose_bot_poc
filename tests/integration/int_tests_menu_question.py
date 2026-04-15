import pytest
from tests.integration.conftest import invoke, get_tool_messages


@pytest.mark.integration
class TestMenuQuestion:

    def test_menu_question_what_do_you_have(self, thread_id):
        result = invoke("What's on the menu?", thread_id)
        assert result["structured_response"].intent == "menu_question"
        tool_msgs = get_tool_messages(result, "answer_menu_question")
        assert len(tool_msgs) > 0
        content = tool_msgs[0].content
        assert "Cheese Brrrrrrrrger" in content
        assert "Chicken Brrrrrrrrito" in content
        assert "Frozen Fries" in content
        assert "Shakes" in content

    def test_menu_question_price_inquiry(self, thread_id):
        result = invoke("How much does the shake cost?", thread_id)
        assert result["structured_response"].intent == "menu_question"
        tool_msgs = get_tool_messages(result, "answer_menu_question")
        assert len(tool_msgs) > 0
        assert "$3.95" in tool_msgs[0].content

    def test_menu_question_calories_inquiry(self, thread_id):
        result = invoke("What are the calories for the burger?", thread_id)
        assert result["structured_response"].intent == "menu_question"
        tool_msgs = get_tool_messages(result, "answer_menu_question")
        assert len(tool_msgs) > 0
        assert "550 cal" in tool_msgs[0].content

    def test_menu_question_vague_food_reference(self, thread_id):
        result = invoke("Do you have anything to eat?", thread_id)
        assert result["structured_response"].intent != "off_topic"
        assert result["structured_response"].response
