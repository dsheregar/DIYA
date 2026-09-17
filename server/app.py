"""DIYA's local API server.

Wires the Mediator, Memory, and ModelRuntime together and exposes them
over HTTP. Runs entirely offline once agent models are downloaded per
agents/registry.yaml.
"""
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import config
from mediator import Mediator
from memory import Memory
from model_runtime import ModelRuntime

model_runtime = ModelRuntime()
memory = Memory()
mediator = Mediator(model_runtime, memory)

app = FastAPI(title="DIYA")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def require_api_key(x_api_key: str | None = Header(default=None)):
    if config.API_KEY and x_api_key != config.API_KEY:
        raise HTTPException(status_code=401, detail="invalid or missing API key")


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    reply: str
    session_id: str
    agent: str
    governance: dict | None = None


class FactRequest(BaseModel):
    fact: str
    source: str
    source_detail: str = ""
    confidence: str = "medium"
    refresh_by: float | None = None


@app.get("/health")
def health():
    return {"status": "ok", "agents": model_runtime.status()}


@app.post("/chat", response_model=ChatResponse, dependencies=[Depends(require_api_key)])
def chat(req: ChatRequest):
    return mediator.handle(req.message, req.session_id)


@app.get("/memory", dependencies=[Depends(require_api_key)])
def query_memory(q: str, limit: int = 10):
    return memory.query(q, limit)


@app.post("/memory", dependencies=[Depends(require_api_key)])
def add_memory(req: FactRequest):
    fact_id = memory.add_fact(req.fact, req.source, req.source_detail, req.confidence, req.refresh_by)
    return {"id": fact_id}
