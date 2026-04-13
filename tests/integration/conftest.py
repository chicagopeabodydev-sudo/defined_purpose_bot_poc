import os
import uuid
import pytest
from dotenv import load_dotenv

load_dotenv()

if not os.getenv("ANTHROPIC_API_KEY"):
    pytest.skip("ANTHROPIC_API_KEY not set", allow_module_level=True)

from src.agents.supervisor import supervisor as _supervisor


def invoke(user_input: str, thread_id: str) -> dict:
    return _supervisor.invoke(
        {"messages": [{"role": "user", "content": user_input}]},
        config={"configurable": {"thread_id": thread_id}},
    )


def get_tool_messages(result: dict, tool_name: str) -> list:
    return [m for m in result["messages"] if hasattr(m, "name") and m.name == tool_name]


@pytest.fixture
def thread_id():
    return str(uuid.uuid4())
