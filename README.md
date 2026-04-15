# Shiver Shack Order Bot

A proof-of-concept chat interface that guides a customer through a fast-food order. Built with a deliberate constraint: **minimize LLM calls** by routing to predefined responses wherever possible — the LLM is only used to classify input and synthesize order summaries.

---

## What It Does

1. Greets the customer and prompts them to start their order
2. Accepts order entries, menu questions, or detects off-topic input
3. Routes each turn via a **supervisor agent** that classifies intent into one of three buckets:
   - `order_entry` — parse and save the menu item(s) and quantity
   - `menu_question` — answer using menu/restaurant knowledge
   - `off_topic` — respond with a contextual redirect; end the conversation after too many strikes
4. Presents a summary of the completed order

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.14 |
| Agent orchestration | LangGraph + LangChain |
| LLM provider | Anthropic API |
| Data models | Pydantic |
| API server | FastAPI + Uvicorn |
| Remote tracing | LangSmith (`shiver-shack-bot` project) |

---

## Project Structure

```
src/
├── agents/        # Supervisor agent — classifies intent and routes to tools
├── middleware/    # After-model hooks: off-topic tracking, per-turn logging
├── tools/         # One function per tool (take_order, summarize, etc.)
├── models/        # Pydantic models: OrderEntry, CompleteOrder, ChatResponse
├── resources/     # Static JSON: menu, error messages, non-error messages
└── main.py        # Entry point: logging setup, env vars, REPL loop

tests/
├── unit/          # Unit tests (prefix: tests_)
└── integration/   # Integration tests (prefix: int_tests_)
```

---

## Design Goals

- **Limit scope** — users can only place/modify an order or ask menu questions; everything else is off-topic
- **Short-circuit the LLM** — predefined responses are selected from resource files for most turns; the LLM only classifies input and writes summaries
- **Success** — a user completes an order (ideally in ≤ 4 exchanges) and confirms the final summary

---

## Setup

1. Copy `.env.example` to `.env` and fill in your `ANTHROPIC_API_KEY`
2. Optionally set `LANGCHAIN_TRACING_V2=true` and `LANGCHAIN_API_KEY` for LangSmith tracing
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the bot:
   ```bash
   python src/main.py
   ```

---

## Off-Topic Handling

Off-topic input is categorized into one of four types and gets a targeted redirect response:

| Type | Description |
|---|---|
| `simply-unrelated` | Generic input unrelated to ordering |
| `not-understandable` | Input that cannot be interpreted |
| `prompt-engineering` | Attempts to manipulate or re-prompt the AI |
| `sexual-content` | Crude or inappropriate language |

After **3 off-topic turns**, the conversation ends automatically.

---

## Logging

Two complementary logging layers run in parallel:

- **LangSmith** — remote tracing of every supervisor invocation (prompts, tool calls, latency, token usage)
- **Domain-state middleware** — local `INFO` log per turn showing intent, off-topic count, tool call count, and a response preview
