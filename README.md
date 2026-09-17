# DIYA
Digital Intelligence for Your Abode

DIYA is a personal, offline-capable, **multi-agent** AI assistant. Instead
of one large model, a mediator routes each request to a small,
purpose-fit model — coding, data analysis, data gathering, creative,
vision — with a lightweight governance layer (ethics/efficiency/debate)
that only kicks in for risky or ambiguous requests. Everything runs
locally via `llama.cpp`, so DIYA works with no internet connection once
the agent models are downloaded.

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the full design
and [`docs/ROADMAP.md`](docs/ROADMAP.md) for current status and next
steps.

## Project layout

```
agents/   registry.yaml — the agent list: model, role, resident policy
server/   FastAPI app: mediator, memory (SQLite fact store), governance
          triage gate, and the model runtime that loads/swaps GGUF models
web/      minimal static chat UI that talks to the server
docs/     architecture notes and roadmap
```

## Hardware target

A single Raspberry Pi 5, 16GB RAM (already owned) — no additional
hardware required. See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md#hardware)
for why, and what an AI HAT+2/NPU would add later if wanted.

## Status

Early scaffold — orchestration code is in place, no agent model weights
are downloaded yet. See [`docs/ROADMAP.md`](docs/ROADMAP.md) Phase 1 for
the current step.
