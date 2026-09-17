# Architecture

DIYA is a **multi-agent** personal assistant, not a single merged model.
Each agent uses whichever small model fits its job — these span
different model families (Qwen2.5, Qwen2.5-Coder, Phi-3 Mini), which
rules out weight-level merging: `mergekit` only works across fine-tunes
of the *same* base model/tokenizer, and this design deliberately doesn't
use one.

## Layers

```
                         ┌─────────────────────┐
  user (web/API) ──────► │      Mediator        │  entry point, routing,
                         │  (checks Memory      │  triage gate, final
                         │   first)             │  answer synthesis
                         └──────────┬───────────┘
                                    │
                 ┌──────────────────┼───────────────────┐
                 ▼                  ▼                    ▼
          ┌─────────────┐   ┌──────────────┐     ┌───────────────┐
          │  Capability  │   │  Governance  │     │    Memory      │
          │    agents    │   │   (triage    │     │  (SQLite fact  │
          │ coding, data_│   │  gate only   │     │  store w/      │
          │ analysis,    │   │  when task   │     │  provenance)   │
          │ data_gather- │   │  is risky/   │     └───────────────┘
          │ ing, creative│   │  ambiguous)  │
          │ , vision     │   │ ethics,      │
          └─────────────┘   │ efficiency,  │
                             │ debate       │
                             └──────────────┘
```

1. **Infrastructure** — `mediator`, `memory`. The mediator is the only
   thing the outside world (web UI, API clients) talks to.
2. **Capabilities** — `coding`, `data_analysis`, `data_gathering`,
   `creative`, `vision`. Reusable, domain-agnostic skills; not domain
   experts. `data_gathering` is the *only* agent allowed to reach the
   internet or local files.
3. **Governance** — `ethics`, `efficiency`, `debate`. Only invoked when
   the mediator's triage gate (`server/governance.py::needs_governance`)
   flags a request as irreversible, touching another person, based on
   low-confidence data, or ambiguous. Routine actions skip this
   entirely — no reason to pay for a full review on "what time is it."
4. **Personas** (future, empty for now) — domain "characters" (travel,
   home automation, etc.) layered on top of the capabilities, defined in
   `agents/registry.yaml`.

## Data flow: Gathering vs. Memory

- `data_gathering` = goes out and gets things, verifies across sources
  when it matters, pushes results into `memory` with
  source/confidence/timestamp metadata.
- `memory` = stores and serves (SQLite, see `server/memory.py`). The
  mediator checks memory *first*, before ever invoking data_gathering —
  cache-then-fetch.
- Every fact carries provenance so staleness/bias is a property of the
  data itself, not a separate fact-checking pass.

## Model runtime

`server/model_runtime.py` loads GGUF models via `llama-cpp-python`.
Agents marked `keep_resident: true` in `agents/registry.yaml` (mediator,
memory, efficiency) stay loaded; the rest load on first use and get
evicted LRU-style once more than `MAX_SWAPPED` non-resident models are
loaded, to keep RAM bounded. Agents that share a `model_id` (e.g.
`mediator`, `data_gathering`, and `ethics` all use Qwen2.5-3B-Instruct)
share one loaded instance instead of duplicating it in RAM.

## Hardware

**Single Raspberry Pi 5, 16GB RAM** (already owned) — no AI HAT+2/NPU
for now, since that's an added cost. 16GB gives enough headroom to keep
2-3 small models resident at once without an accelerator; everything
(including what the original design put on an NPU — memory, efficiency,
vision) runs on the Pi's own CPU. `vision` will be noticeably slower
without dedicated acceleration; that's an acceptable tradeoff to start,
and an AI HAT+2 remains a clean future upgrade if/when it makes sense to
buy one — nothing here architecturally depends on not having it.
