import os
import sys
import uuid
import json
import logging
import random
from dotenv import load_dotenv
from langchain_core.runnables import RunnableConfig

load_dotenv()

log_file = os.getenv("LOG_FILE") or None
log_level = os.getenv("LOG_LEVEL", "INFO").upper()

logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
    filename=log_file,
    encoding="utf-8" if log_file else None,
)

from src.agents.supervisor import supervisor

_NON_ERROR_PATH = os.path.join(os.path.dirname(__file__), "resources", "non_error_messages.json")

def _get_greeting() -> str:
    with open(_NON_ERROR_PATH) as f:
        messages = json.load(f)
    matches = [m for m in messages if m.get("messageType") == "greeting"]
    return random.choice(matches)["message"] if matches else "Welcome to Shiver Shack!"


def run():
    thread_id = str(uuid.uuid4())
    config: RunnableConfig = {"configurable": {"thread_id": thread_id}}

    print(_get_greeting())

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            sys.exit(0)

        if not user_input:
            continue

        result = supervisor.invoke(
            {"messages": [{"role": "user", "content": user_input}]},
            config=config,
        )

        structured = result.get("structured_response")
        last_message = result["messages"][-1]

        if structured:
            response_text = structured.response
        else:
            response_text = last_message.content

        print(f"\nEmployee: {response_text}\n")

        if hasattr(last_message, "content") and "Goodbye" in last_message.content:
            sys.exit(0)


if __name__ == "__main__":
    run()
