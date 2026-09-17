# Roadmap

## Phase 1 — Pick merge candidates (current step)
Find 2-3 Llama-3.2-3B-Instruct fine-tunes on Hugging Face that share the
exact same base architecture and tokenizer (required for weight merging).
`scripts/find_compatible_models.py` queries the HF API for models tagged
with a given `base_model`. Fill the results into `merge/mergekit_config.yaml`.

## Phase 2 — Merge
Run `mergekit-yaml merge/mergekit_config.yaml ./merged-model` (TIES or
DARE-TIES method) to produce a merged set of weights.

## Phase 3 — Convert & quantize
Use `llama.cpp`'s `convert_hf_to_gguf.py` to turn the merged model into
GGUF, then `llama-quantize` to produce a Q4_K_M (or similar) quantized
file small enough for CPU / Raspberry Pi 5 inference.

## Phase 4 — Local API server
`server/app.py` (FastAPI + `llama-cpp-python`) loads the quantized GGUF
and exposes:
- `GET /health`
- `POST /chat` — send a message, get a reply (keeps simple in-memory
  conversation state per session)

## Phase 5 — Web UI
`web/index.html` — a minimal static chat page that calls the API.
Can be served by any static file host or opened directly.

## Phase 6 — Remote access
Add API key auth to the server, then expose it beyond localhost (e.g.
Tailscale, a reverse proxy with HTTPS, or a tunneling service) so other
apps/devices can reach DIYA remotely.

## Phase 7 — Raspberry Pi 5 deployment
Move the quantized model + server onto the Pi 5, run `llama-cpp-python`
built for ARM, and confirm latency/throughput is acceptable.
