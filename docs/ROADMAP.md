# Roadmap

## Phase 1 — Get real models downloaded (current step)
Verify the exact HF repo/file names in `agents/registry.yaml` (some are
marked VERIFY) and download the GGUF files for `mediator`, `memory`, and
one capability agent (start with `coding` or `data_gathering`) into
`models/`. Confirm `server/model_runtime.py` loads them and `/health`
reports them as loaded.

## Phase 2 — Wire up real routing
Replace `mediator.py`'s keyword-based `classify_intent` with the
mediator's own model doing intent classification (structured
JSON output: which agent(s) to call, in what order). Keep the keyword
router as a fallback.

## Phase 3 — Fill out the remaining agents
Download models for `data_analysis`, `creative`, `ethics`, `efficiency`,
`debate`. Test the governance triage gate end-to-end (an irreversible or
other-person-touching request should trigger Ethics -> Efficiency ->
Debate).

## Phase 4 — Memory quality
Add embedding-based semantic search to `server/memory.py` (currently
substring search only) so recall doesn't depend on exact wording.

## Phase 5 — Vision agent
Pick and wire up a CPU-friendly detection model (quantized YOLOv8n or
similar) for person/object detection. Defer person *identification*
pending a legal review (BIPA and similar).

## Phase 6 — Web UI + remote access
Extend `web/` to show which agent answered and surface governance notes
when present. Add real API-key enforcement and a private access method
(e.g. Tailscale) before reaching it from outside the home network.

## Phase 7 — Raspberry Pi 5 deployment
Move `models/`, `data/`, and the server onto the Pi 5 (16GB, already
owned), confirm `llama-cpp-python` runs well on ARM, and measure
resident/swap latency in practice — this determines whether the
`MAX_SWAPPED` / `keep_resident` settings in `agents/registry.yaml` need
tuning for that hardware.

## Deferred / open items
- Personas layer (travel, home automation, hobby-specific "characters")
- Expansion nodes (additional Pi boards per persona) — not needed while
  running on the single owned Pi 5
- AI HAT+2 / NPU offload — clean upgrade path later, not required now
- Glasses/AR client — a future device endpoint, not a new architecture
