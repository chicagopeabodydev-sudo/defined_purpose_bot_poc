import os
import sys
import uuid
import logging
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

GREETING = (
    "Welcome to Shiver Shack - home of the Cheese-Burrrrrrrr-ger.\n"
    "What can I get you?\n"
)


def run():
    thread_id = str(uuid.uuid4())
    config: RunnableConfig = {"configurable": {"thread_id": thread_id}}

    print(GREETING)

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
