import os
import json
import uuid
import time
import random
import logging
import concurrent.futures
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)

logger = logging.getLogger(__name__)


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


def _request_logger(thread_id: str) -> logging.LoggerAdapter:
    return logging.LoggerAdapter(logger, {"thread_id": thread_id})


from src.agents.supervisor import supervisor

_BASE = Path(__file__).parent
_TIMEOUT = int(os.getenv("INVOKE_TIMEOUT_SECONDS", "30"))
_FALLBACK = "Sorry, something went wrong — I couldn't process that. Please try again."
_NON_ERROR_PATH = _BASE / "resources" / "non_error_messages.json"


def _get_greeting() -> str:
    with open(_NON_ERROR_PATH) as f:
        messages = json.load(f)
    matches = [m for m in messages if m.get("messageType") == "greeting"]
    return random.choice(matches)["message"] if matches else "Welcome to Shiver Shack!"


app = FastAPI(title="Shiver Shack API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    thread_id: str
    message: str


class GreetResponse(BaseModel):
    thread_id: str
    message: str


class ChatResponse(BaseModel):
    message: str
    end_conversation: bool


@app.get("/api/greet", response_model=GreetResponse)
def greet():
    thread_id = str(uuid.uuid4())
    log = _request_logger(thread_id)
    log.info("GET /api/greet — request received, assigned thread_id=%s", thread_id)
    message = _get_greeting()
    log.info("GET /api/greet — response sent message_type=greeting")
    return GreetResponse(thread_id=thread_id, message=message)


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    log = _request_logger(req.thread_id)
    log.info("POST /api/chat — request received message=%.80r", req.message)
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
            log.error("POST /api/chat — supervisor timeout after %.0fms", elapsed_ms)
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


# Mount static files AFTER all API routes — only if production build exists
_DIST = Path("frontend/dist")
if _DIST.exists():
    app.mount("/", StaticFiles(directory=str(_DIST), html=True), name="static")
