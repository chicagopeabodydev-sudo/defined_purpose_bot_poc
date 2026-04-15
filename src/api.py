import os
import json
import uuid
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
    message = _get_greeting()
    return GreetResponse(thread_id=thread_id, message=message)


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    config = {"configurable": {"thread_id": req.thread_id}}
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(
            supervisor.invoke,
            {"messages": [{"role": "user", "content": req.message}]},
            config,
        )
        try:
            result = future.result(timeout=_TIMEOUT)
        except concurrent.futures.TimeoutError:
            raise HTTPException(status_code=503, detail=_FALLBACK)
    structured = result.get("structured_response")
    last_message = result["messages"][-1]

    if structured:
        response_text = structured.response
    else:
        response_text = last_message.content

    end_conversation = "Goodbye" in last_message.content
    return ChatResponse(message=response_text, end_conversation=end_conversation)


# Mount static files AFTER all API routes — only if production build exists
_DIST = Path("frontend/dist")
if _DIST.exists():
    app.mount("/", StaticFiles(directory=str(_DIST), html=True), name="static")
