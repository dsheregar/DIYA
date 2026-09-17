# DIYA
Digital Intelligence for Your Abode

DIYA is a personal, offline-capable AI assistant built by merging a few
small open-weight language models into one, then serving that merged
model through your own API and web interface.

## How it works

1. **Merge** — combine a few same-family open-weight instruct/fine-tuned
   models (same base architecture + tokenizer) into a single model using
   [`mergekit`](https://github.com/arcee-ai/mergekit). See [`merge/`](merge/).
2. **Quantize** — convert the merged model to GGUF and quantize it with
   `llama.cpp` so it can run on modest hardware (CPU today, a Raspberry
   Pi 5 later).
3. **Serve** — run the quantized model locally with `llama-cpp-python`
   behind a small FastAPI server. See [`server/`](server/).
4. **Use it** — a minimal web chat UI ([`web/`](web/)) talks to the API,
   and the same API can be reached remotely (once you add auth/tunneling)
   from other apps.

Because everything runs from local weights via `llama.cpp`, DIYA works
with **no internet connection** once the model is downloaded and merged.

## Chosen base model

**Llama 3.2 3B-Instruct** — Meta built the 1B/3B Llama 3.2 models
specifically for on-device/edge use cases, it's well supported by
`llama.cpp` (including on ARM/Raspberry Pi), and there's a healthy pool
of compatible fine-tunes to merge.

## Project layout

```
merge/    mergekit config + instructions for producing the merged model
server/   FastAPI server that loads the local GGUF model and exposes /chat
web/      minimal static chat UI that talks to the server
docs/     architecture notes and roadmap
```

## Status

Early scaffold — no model weights are downloaded yet. See
[`docs/ROADMAP.md`](docs/ROADMAP.md) for the plan and current step.
