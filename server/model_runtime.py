"""Loads and swaps GGUF models for agents, per agents/registry.yaml.

Agents that share a model_id share one loaded instance. Agents marked
keep_resident stay loaded; others are loaded on first use and evicted
LRU-style once more than MAX_SWAPPED non-resident models are loaded at
once (keeps RAM bounded on the Pi).
"""
import threading
import time
from pathlib import Path

import yaml

MAX_SWAPPED = 2
MAX_REPLY_TOKENS = 700  # caps generation time on CPU-only hardware

REGISTRY_PATH = Path(__file__).parent.parent / "agents" / "registry.yaml"
MODELS_DIR = Path(__file__).parent.parent / "models"


class ModelRuntime:
    def __init__(self, registry_path: Path = REGISTRY_PATH, models_dir: Path = MODELS_DIR):
        self.agents: dict[str, dict] = {}
        self.resident_ids: set[str] = set()
        self.models_dir = models_dir
        self._loaded: dict[str, object] = {}  # model_id -> Llama instance
        self._last_used: dict[str, float] = {}  # model_id -> timestamp
        self._load_registry(registry_path)
        # llama-cpp-python's underlying context isn't safe for concurrent
        # access, and FastAPI's sync endpoints run in a thread pool - this
        # serializes every load/evict/generate across the whole server.
        # Fine for a single-user assistant on CPU: only one inference makes
        # sense at a time anyway on this hardware.
        self._lock = threading.Lock()

    def _load_registry(self, path: Path):
        data = yaml.safe_load(path.read_text())
        for layer in data.get("layers", {}).values():
            for agent in layer:
                self.agents[agent["name"]] = agent
                if agent.get("keep_resident"):
                    self.resident_ids.add(agent["model_id"])

    def agent_config(self, agent_name: str) -> dict:
        if agent_name not in self.agents:
            raise KeyError(f"unknown agent: {agent_name}")
        return self.agents[agent_name]

    def status(self) -> dict:
        return {
            name: {
                "model_id": cfg.get("model_id"),
                "loaded": cfg.get("model_id") in self._loaded,
                "keep_resident": bool(cfg.get("keep_resident")),
            }
            for name, cfg in self.agents.items()
        }

    def get(self, agent_name: str):
        """Return a loaded Llama instance for this agent, loading/evicting as needed.

        Only safe to call while holding self._lock - use generate() instead
        unless you already hold it.
        """
        cfg = self.agent_config(agent_name)
        model_id = cfg.get("model_id")
        if not model_id:
            raise ValueError(f"agent '{agent_name}' has no model configured yet")

        self._last_used[model_id] = time.time()
        if model_id in self._loaded:
            return self._loaded[model_id]

        self._evict_if_needed(model_id)
        self._loaded[model_id] = self._load(cfg)
        return self._loaded[model_id]

    def generate(self, agent_name: str, messages: list[dict]) -> str:
        """Load (if needed) and run chat completion for this agent, fully
        serialized against every other agent call on the server."""
        with self._lock:
            llm = self.get(agent_name)
            response = llm.create_chat_completion(messages=messages, max_tokens=MAX_REPLY_TOKENS)
            return response["choices"][0]["message"]["content"]

    def _evict_if_needed(self, incoming_model_id: str):
        swapped = [m for m in self._loaded if m not in self.resident_ids]
        if len(swapped) < MAX_SWAPPED:
            return
        oldest = min(swapped, key=lambda m: self._last_used.get(m, 0))
        del self._loaded[oldest]

    def _load(self, cfg: dict):
        from llama_cpp import Llama

        model_path = self.models_dir / cfg["model_file"]
        return Llama(model_path=str(model_path), n_ctx=8192, verbose=False)
