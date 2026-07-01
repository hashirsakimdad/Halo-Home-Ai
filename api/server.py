"""FastAPI REST server with health monitoring."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import BaseModel

from core.llm import LLMClient
from core.logging_setup import setup_logging
from core.orchestrator import Orchestrator
from config.settings import API_HOST, API_PORT

logger = logging.getLogger(__name__)

orchestrator: Orchestrator | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize shared services on startup."""
    global orchestrator
    setup_logging()
    orchestrator = Orchestrator()
    logger.info("HoloHome API started")
    yield
    logger.info("HoloHome API shutting down")


app = FastAPI(title="HoloHome AI", version="0.1.0", lifespan=lifespan)


class ChatRequest(BaseModel):
    """Incoming chat request body."""

    message: str
    context: dict | None = None


class ChatResponse(BaseModel):
    """Chat response with routing metadata."""

    response: str
    agent: str | None = None


@app.get("/health")
async def health():
    """Return system health status for monitoring and systemd checks."""
    llm = LLMClient()
    ollama_ok = await llm.is_available()
    status = "healthy" if ollama_ok else "degraded"
    return {
        "status": status,
        "ollama": ollama_ok,
        "service": "holohome",
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process a text message through the orchestrator."""
    if orchestrator is None:
        return ChatResponse(response="Service not ready.", agent=None)
    response = await orchestrator.run(request.message, request.context)
    return ChatResponse(response=response, agent=None)


def run_server() -> None:
    """Launch uvicorn with configured host and port."""
    import uvicorn

    setup_logging()
    uvicorn.run("api.server:app", host=API_HOST, port=API_PORT, reload=False)
