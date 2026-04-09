# Plan: Logging Strategy — LangSmith + Domain-State Middleware

## Context
The project has no logging in place. During development it is difficult to observe how the supervisor agent classifies user input, how often off-topic messages occur, and whether tool calls are behaving correctly. The goal is to add two complementary layers of observability:
1. **LangSmith** — automatic, zero-code tracing of all LangChain internals (model calls, tool calls, token usage, structured output)
2. **`after_model` middleware logger** — lightweight, domain-aware local log capturing intent classification and off-topic count per turn

---

## Layer 1 — LangSmith (no code changes required)

LangSmith is already wired into the project via `.env`. Enabling it is a one-line change to that file.

**File to change:** `.env`

```
LANGCHAIN_TRACING_V2=true        # change false → true
LANGCHAIN_API_KEY=<already set>
LANGCHAIN_PROJECT=shiver-shack-bot
```

Once enabled, every `supervisor.invoke()` call automatically sends a trace to LangSmith containing:
- Full model prompt and response (including system prompt)
- `SupervisorDecision` structured output per turn
- Tool call name, inputs, and outputs
- Latency and token usage per step

No changes to Python source are needed for this layer.

---

## Layer 2 — Domain-State Middleware Logger

A new `log_decision` middleware function added to `src/middleware/off_topic_tracker.py` alongside the existing `track_off_topic` hook.

Uses Python's stdlib `logging` module as the output sink — no new dependencies.

### What gets logged per turn
| Field | Source |
|---|---|
| `intent` | `structured_response.intent` from `SupervisorDecision` |
| `off_topic_count` | `state.get("off_topic_count", 0)` |
| `response_preview` | First 120 chars of the last `AIMessage` content |
| `tool_calls` | Count of tool calls in the last model response |

### Implementation

**`src/middleware/off_topic_tracker.py`** — add below the existing `track_off_topic` function:

```python
import logging
from langchain_core.messages import AIMessage

logger = logging.getLogger(__name__)

@after_model(state_schema=OrderState)
def log_decision(state: OrderState, runtime: Runtime) -> None:
    last = state["messages"][-1]
    structured = state.get("structured_response")
    tool_calls = len(getattr(last, "tool_calls", []))
    logger.info(
        "intent=%-15s off_topic=%d tool_calls=%d | %.120s",
        structured.intent if structured else "unknown",
        state.get("off_topic_count", 0),
        tool_calls,
        last.content if isinstance(last, AIMessage) else "",
    )
```

**`src/agents/supervisor.py`** — add `log_decision` to the middleware list:

```python
from src.middleware.off_topic_tracker import track_off_topic, log_decision

supervisor = create_agent(
    ...
    middleware=[track_off_topic, log_decision],   # log_decision runs after track_off_topic
    ...
)
```

**`src/main.py`** — configure the root logger at startup (after `load_dotenv()`):

```python
import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
```

---

## Files Modified

| File | Change |
|---|---|
| `.env` | `LANGCHAIN_TRACING_V2=false` → `true` |
| `src/middleware/off_topic_tracker.py` | Add `log_decision` after_model hook |
| `src/agents/supervisor.py` | Add `log_decision` to middleware list |
| `src/main.py` | Add `logging.basicConfig(...)` after `load_dotenv()` |

No new dependencies. No new files.

---

## Verification

1. Set `LANGCHAIN_TRACING_V2=true` in `.env` and run `python -m src.main`
2. Send a valid order — confirm LangSmith trace appears at smith.langchain.com under project `shiver-shack-bot` showing intent `order_entry`, tool call to `take_order`, and token usage
3. Send a menu question — confirm intent `menu_question` in both LangSmith and local log output
4. Send off-topic input — confirm local log shows `off_topic=1`, LangSmith shows `[OFF-TOPIC]` marker in model response
5. Send off-topic input 2 more times — confirm conversation terminates and `off_topic=3` appears in final log line

---

## Configure file location and log-level variables

### Goal
Allow `LOG_FILE` and `LOG_LEVEL` to be set in `.env` so that log output and verbosity can be controlled without touching source code. When `LOG_FILE` is empty or unset, behavior defaults to stderr (preserving the current behavior).

---

### Changes Required

**`.env`** — add two new variables below the existing logging block:

```
LOG_FILE=          # empty → stderr; set a path (e.g. logs/bot.log) to write to a file
LOG_LEVEL=INFO     # DEBUG | INFO | WARNING | ERROR — controls verbosity
```

**`src/main.py`** — replace the current `logging.basicConfig(...)` block with the configurable version:

```python
import os

log_file = os.getenv("LOG_FILE") or None          # empty string treated as unset
log_level = os.getenv("LOG_LEVEL", "INFO").upper()

logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
    filename=log_file,
    encoding="utf-8" if log_file else None,
)
```

`import os` can be added to the existing import block — no new top-level import is needed if `os` is already present.

---

### Files Modified

| File | Change |
|---|---|
| `.env` | Add `LOG_FILE=` and `LOG_LEVEL=INFO` |
| `src/main.py` | Replace `logging.basicConfig(...)` with env-driven version; add `os.getenv` calls |

No new dependencies. No new files.

---

### Behavior Matrix

| `LOG_FILE` | `LOG_LEVEL` | Result |
|---|---|---|
| empty / unset | `INFO` | Logs to stderr at INFO (current behavior) |
| empty / unset | `DEBUG` | Logs to stderr at DEBUG (verbose) |
| `logs/bot.log` | `INFO` | Logs to file at INFO; nothing printed to terminal |
| `logs/bot.log` | `WARNING` | Logs to file at WARNING; INFO lines from `log_decision` suppressed |

---

### Verification

1. Leave `LOG_FILE` empty, run `python -m src.main` — confirm log lines appear in the terminal (stderr)
2. Set `LOG_LEVEL=DEBUG`, re-run — confirm additional DEBUG output from LangChain internals appears
3. Set `LOG_FILE=logs/bot.log`, re-run — confirm nothing logged to terminal and the file is created with log lines
4. Set `LOG_LEVEL=WARNING` with a file path — confirm `log_decision` INFO lines do not appear in the file
