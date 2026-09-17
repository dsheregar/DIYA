"""DIYA's local API server.

Loads a quantized GGUF model with llama-cpp-python and exposes it over
HTTP. Runs entirely offline once the model file is present locally.
"""
import uuid
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import config

_llm = None
_conversations: dict[str, list[dict]] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _llm
    try:
        from llama_cpp import Llama

        _llm = Llama(
            model_path=config.MODEL_PATH,
            n_ctx=config.CONTEXT_SIZE,
            n_threads=config.THREADS,
            verbose=False,
        )
    except (ImportError, ValueError, FileNotFoundError) as e:
        print(f"[DIYA] model not loaded ({e}) - /chat will 503 until one is set up")
        _llm = None
    yield
    _llm = None


app = FastAPI(title="DIYA", lifespan=lifespan)

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


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": _llm is not None}


@app.post("/chat", response_model=ChatResponse, dependencies=[Depends(require_api_key)])
def chat(req: ChatRequest):
    if _llm is None:
        raise HTTPException(status_code=503, detail="model not loaded yet")

    session_id = req.session_id or str(uuid.uuid4())
    history = _conversations.setdefault(
        session_id, [{"role": "system", "content": config.SYSTEM_PROMPT}]
    )
    history.append({"role": "user", "content": req.message})

    result = _llm.create_chat_completion(messages=history)
    reply = result["choices"][0]["message"]["content"]
    history.append({"role": "assistant", "content": reply})

    return ChatResponse(reply=reply, session_id=session_id)
