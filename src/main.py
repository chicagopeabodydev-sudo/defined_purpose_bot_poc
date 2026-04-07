import sys
import uuid
from dotenv import load_dotenv
from langchain_core.runnables import RunnableConfig

load_dotenv()

from src.agents.supervisor import supervisor

GREETING = (
    "Welcome to Shiver Shack! It's so cold in here you'll shiver off \n"
    "every calorie you eat — basically a free meal. \n"
    "What can I get you? (We have burgers, burritos, fries, and shakes.)\n"
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
