import os

MODEL_PATH = os.environ.get("DIYA_MODEL_PATH", "../models/diya.Q4_K_M.gguf")
CONTEXT_SIZE = int(os.environ.get("DIYA_CONTEXT_SIZE", "4096"))
THREADS = int(os.environ.get("DIYA_THREADS", str(os.cpu_count() or 4)))
API_KEY = os.environ.get("DIYA_API_KEY")  # set this before exposing the server beyond localhost
SYSTEM_PROMPT = os.environ.get(
    "DIYA_SYSTEM_PROMPT",
    "You are DIYA, a helpful personal assistant running locally on the user's own hardware.",
)
