# CLAUDE.md

## Project
Chat interface to guide a customer through a food order. This can include a "main" food item, side item, and/or drink. When the order is complete a summary is presented.

## Stack
- Python v 3.14
- LangGraph and LangChain for Agents, Tools, and Middleware
- Anthropic API (API key is an environmental variable)
- Pydantic for all data models

## Structure

The codebase is organized into four layers under `src/`:

- **agents/** — The supervisor agent (`supervisor.py`) is the central routing hub. It classifies user input into `order_entry`, `menu_question`, or `off_topic` via `SupervisorDecision` structured output and delegates to the appropriate tool.
- **middleware/** — `after_model` hooks that run after every model response. Currently: `track_off_topic` (enforces the 3-strike off-topic limit) and `log_decision` (emits a structured INFO log per turn).
- **tools/** — One function per tool, called by the supervisor: `take_order`, `answer_menu_question`, `get_error_response`, `get_non_error_response`, `summarize_order`.
- **models/** — Pydantic `BaseModel` definitions: `OrderEntry`, `CompleteOrder`, `ChatResponse`.
- **resources/** — Static JSON files loaded at runtime: `menu.json`, `error_messages.json`, `non_error_messages.json`.

`src/main.py` is the entry point: initializes logging, loads env vars, and runs the REPL loop.

## Testing Goals
1. Unit tests should be created for all functions
  - tests for valid and invalid input values
  - success path and error path shoud have tests
  - verify response values for common and uncommon scenarios
  - unit tests names have a prefix of "tests_" followed by what is being tested
  - unit tests go in a folder "./tests/unit/"
  - unit tests are always checked after any changes to the functions under test
2. Do not automatically fix broken unit tests
  - they likely broke due to an unexpected side effect of a recent change
  - when unit tests fail try to discover the root cause and propose solution(s)
3. Integration should be created that cover the key steps in placing an order
  - tests for valid and invalid input values
  - success path and error path shoud have tests
  - verify response values for common and uncommon scenarios
  - integration tests names have a prefix of "int_tests_" followed by what is being tested
  - integration tests go in a folder "./tests/integration/"
  - request approval before running integration test

## Logging Strategy

Two complementary layers are active. Do not remove either layer without discussion.

### Layer 1 — LangSmith (remote tracing)
- Controlled by `LANGCHAIN_TRACING_V2=true` in `.env`
- Project name: `shiver-shack-bot` (visible at smith.langchain.com)
- Automatically captures every `supervisor.invoke()` call: full prompt/response, `SupervisorDecision` structured output, tool name + inputs + outputs, latency, token usage
- No code changes needed to produce or read these traces — toggle the `.env` flag to enable/disable

### Layer 2 — Domain-state middleware logger (local, per-turn)
- Implemented as `log_decision` in [src/middleware/off_topic_tracker.py](src/middleware/off_topic_tracker.py), registered as the second entry in the `supervisor` middleware list (runs after `track_off_topic`)
- Uses Python stdlib `logging` — no extra dependencies
- `logging.basicConfig` is configured in [src/main.py](src/main.py) immediately after `load_dotenv()`; log format: `HH:MM:SS [LEVEL] module — message`
- Each turn emits one `INFO` line with four fields:

| Field | What it contains |
|---|---|
| `intent` | `SupervisorDecision.intent` — `order_entry`, `menu_question`, or `off_topic` |
| `off_topic` | Running count from `state["off_topic_count"]`; resets per thread |
| `tool_calls` | Number of tool calls in the last model message |
| response preview | First 120 chars of the last `AIMessage` content |

### Key relationships
- `off_topic_count` is incremented by `track_off_topic` before `log_decision` runs, so the logged count is always the post-increment value
- When `off_topic_count` reaches `OFF_TOPIC_LIMIT` (3), `track_off_topic` terminates the conversation via `Command(goto="__end__")`; `log_decision` still fires and will log `off_topic=3` on the final turn
- `structured_response` may be `None` on error or early-exit turns; `log_decision` falls back to `intent=unknown` in that case

## Plans are created first
Except for minor fixes and/or changes all modifications will happen in a two-step process:
1. First, a plan will be created that outlines the steps to realize the requested change. Creating this plan may take multiple steps to add clarifications or choose from more than one implementation options. The final plan will be saved to the ./plans folder in a markdown (.md) format.
2. Second, plans will be implemented using the saved plan's markdown file as guidance. After plans are fully implemented, how to test the changes should be provided.

## Do NOT Do This
- Do not proactively make changes to files or code. Except  when explicitly instructed it's OK to make certain changes (for example, typos and/or minor style fixes), assume all changes require approval.

## DO This
- Provide suggestions to make the code better or more efficient.
- Seek approval for suggested changes along with documentation supporting why it is helpful.
- Be a master of the underlying tech stack as outlined above.


## Additional Resources
[Python unit-tests overview](https://docs.python.org/3/library/unittest.html)
[PyTest documentation](https://docs.pytest.org/)
[Project overview](./.claude/skills/project-overview-skill/)