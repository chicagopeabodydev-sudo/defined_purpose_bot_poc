# Observability Improvements Plan

## Context

The codebase has two observability layers already in place: Python stdlib logging (configured in both entry points) and a `log_decision` middleware hook that emits one structured INFO line per agent turn. LangSmith remote tracing is configured via `.env` env vars but `langsmith` is not pinned as a dependency — a fresh install would silently break tracing. Additionally, the API layer and all five tool files have zero logging, creating blind spots in request-level visibility and per-tool call tracing.

This plan adds `langsmith` to requirements, instruments the FastAPI layer with request/response/timing logs, and adds DEBUG-level logging to each tool.

---

## Files Changed

- `requirements.txt`
- `src/api.py`
- `src/main.py`
- `src/tools/take_order.py`
- `src/tools/answer_menu_question.py`
- `src/tools/get_error_response.py`
- `src/tools/get_non_error_response.py`
- `src/tools/summarize_order.py`

---

## Step 1 — requirements.txt

Add `langsmith` after `langgraph`:

```
langsmith
```

LangChain imports `langsmith` at runtime when `LANGCHAIN_TRACING_V2=true`. Without it pinned, a fresh install silently leaves remote tracing broken.

---

## Step 2 — src/api.py: Thread-correlated request/response logging

### 2a. Add imports and module logger

After the existing `logging.basicConfig(...)` block (lines 18–22), add:

```python
import time

logger = logging.getLogger(__name__)
```

### 2b. Add `_SafeFormatter` to support optional `thread_id` field

The API layer will inject `thread_id` into log records via `LoggerAdapter`. Other loggers (middleware, tools) don't set it, so a custom formatter must supply a default `"-"` to avoid `KeyError`.

After the `logger` line:

```python
class _SafeFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        if not hasattr(record, "thread_id"):
            record.thread_id = "-"
        return super().format(record)

_root_handler = logging.root.handlers[0]
_root_handler.setFormatter(
    _SafeFormatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s [%(thread_id)s] — %(message)s",
        datefmt="%H:%M:%S",
    )
)
```

This replaces the formatter on the existing root handler (stream or file) — no handler is added or removed.

### 2c. Add `_request_logger` helper

```python
def _request_logger(thread_id: str) -> logging.LoggerAdapter:
    return logging.LoggerAdapter(logger, {"thread_id": thread_id})
```

### 2d. Instrument `greet()` endpoint

```python
@app.get("/api/greet", response_model=GreetResponse)
def greet():
    thread_id = str(uuid.uuid4())
    log = _request_logger(thread_id)
    log.info("GET /api/greet — request received, assigned thread_id=%s", thread_id)
    message = _get_greeting()
    log.info("GET /api/greet — response sent message_type=greeting")
    return GreetResponse(thread_id=thread_id, message=message)
```

### 2e. Instrument `chat()` endpoint

Add entry log, `time.perf_counter()` timing, timeout error log, and response log:

```python
@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    log = _request_logger(req.thread_id)
    log.info(
        "POST /api/chat — request received message=%.80r",
        req.message,
    )
    config = {"configurable": {"thread_id": req.thread_id}}
    t0 = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(
            supervisor.invoke,
            {"messages": [{"role": "user", "content": req.message}]},
            config,
        )
        try:
            result = future.result(timeout=_TIMEOUT)
        except concurrent.futures.TimeoutError:
            elapsed_ms = (time.perf_counter() - t0) * 1000
            log.error(
                "POST /api/chat — supervisor timeout after %.0fms", elapsed_ms
            )
            raise HTTPException(status_code=503, detail=_FALLBACK)

    elapsed_ms = (time.perf_counter() - t0) * 1000
    structured = result.get("structured_response")
    last_message = result["messages"][-1]
    response_text = structured.response if structured else last_message.content
    end_conversation = "Goodbye" in last_message.content

    log.info(
        "POST /api/chat — response sent elapsed_ms=%.0f end_conversation=%s",
        elapsed_ms,
        end_conversation,
    )
    return ChatResponse(message=response_text, end_conversation=end_conversation)
```

---

## Step 3 — src/main.py: Apply same `_SafeFormatter`

Apply the identical `_SafeFormatter` class and handler replacement after `main.py`'s `logging.basicConfig(...)` block so that REPL log output uses the same format. Tool and middleware logs in the REPL path will show `[-]` for thread_id, which is correct.

No module-level logger needed in `main.py` — the REPL loop prints to stdout; it does not log.

---

## Step 4 — Tool files: Add DEBUG-level logging

Each tool file gets `import logging` and `logger = logging.getLogger(__name__)` below existing imports. Log at DEBUG so these are silent by default (`LOG_LEVEL=INFO`) and visible when `LOG_LEVEL=DEBUG`.

### src/tools/take_order.py
- Entry: `logger.debug("take_order called item=%r quantity=%d", item, quantity)`
- Quantity error: `logger.debug("take_order quantity out of range item=%r quantity=%d", item, quantity)`
- Item not found: `logger.debug("take_order item not on menu item=%r", item)`
- Success: `logger.debug("take_order success item=%r qty=%d price=%.2f", canonical_name, quantity, price)`

### src/tools/answer_menu_question.py
- Entry: `logger.debug("answer_menu_question called question=%.80r", question)`
- Exit: `logger.debug("answer_menu_question returning %d menu items", len(menu))`

### src/tools/get_error_response.py
- Entry: `logger.debug("get_error_response called error_type=%r level=%d", error_type, level)`
- Exit: `logger.debug("get_error_response matched %d candidates error_type=%r level=%d", len(matches), error_type, level)`

### src/tools/get_non_error_response.py
- Entry: `logger.debug("get_non_error_response called message_type=%r", message_type)`
- No-match: `logger.debug("get_non_error_response no match for message_type=%r, using fallback", message_type)`
- Exit: `logger.debug("get_non_error_response matched %d candidates message_type=%r", len(matches), message_type)`

### src/tools/summarize_order.py
- `summarize_order_entry` entry: `logger.debug("summarize_order_entry item=%r quantity=%d", item, quantity)`
- `summarize_complete_order` entry: `logger.debug("summarize_complete_order called with %d items", len(items))`
- `summarize_complete_order` exit: `logger.debug("summarize_complete_order total_price=%.2f total_minutes=%d", total_price, total_minutes)`

---

## What a correlated log sequence looks like

```
12:34:01 [INFO]  src.api [-]                         — POST /api/chat — request received message='I want a burger'
12:34:01 [DEBUG] src.tools.take_order [-]             — take_order called item='burger' quantity=1
12:34:01 [DEBUG] src.tools.take_order [-]             — take_order success item='Shiver Burger' qty=1 price=8.99
12:34:01 [INFO]  src.middleware.off_topic_tracker [-] — intent=order_entry off_topic=0 tool_calls=2 | ...
12:34:02 [INFO]  src.api [abc-123]                   — POST /api/chat — response sent elapsed_ms=1240 end_conversation=False
```

Tool and middleware logs show `[-]` because `thread_id` context is scoped to the `LoggerAdapter` inside the API handler. If full thread_id propagation into tool logs is needed in the future, the mechanism is `contextvars.ContextVar` + a root `logging.Filter` — out of scope for this plan.

---

## Verification

1. Set `LOG_LEVEL=DEBUG` in `.env`
2. Start the API: `uvicorn src.api:app --reload`
3. `GET /api/greet` — verify two INFO lines appear with correct thread_id in the adapter field
4. `POST /api/chat` — verify entry INFO, tool DEBUG lines, middleware INFO, and response INFO with `elapsed_ms`
5. Simulate a timeout (lower `INVOKE_TIMEOUT_SECONDS=1`) — verify ERROR log fires before the 503 response
6. Reset `LOG_LEVEL=INFO` — verify tool DEBUG lines are suppressed, only API INFO and middleware INFO remain
7. Run unit tests: `pytest tests/unit/` — verify no regressions
