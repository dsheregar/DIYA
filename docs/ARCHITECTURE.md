# Architecture

```
 Hugging Face                mergekit                llama.cpp
 fine-tunes  ───────────►  merge (TIES/   ───────►  convert + quantize
 (same base)                DARE-TIES)                    │
                                                            ▼
                                                     merged.Q4_K_M.gguf
                                                            │
                                                            ▼
                                              server/app.py (FastAPI +
                                              llama-cpp-python), local
                                              inference, no internet
                                                    │            │
                                                    ▼            ▼
                                          web/index.html   remote API
                                          (chat UI)        clients
```

## Why weight merging, not an API router

The goal is a single model that runs fully offline (CPU now, Raspberry
Pi 5 later). Closed models (GPT/Claude/Gemini) can't be merged — their
weights aren't public. Merging only works across open-weight models that
share the same base architecture and tokenizer, which is why every model
in `merge/mergekit_config.yaml` must be a fine-tune of the same base
(Llama 3.2 3B-Instruct).

## Why quantized GGUF + llama.cpp

A 3B model at full precision is ~6GB+ and too slow/large for a Pi 5.
Q4_K_M quantization shrinks it to ~2GB with modest quality loss, and
`llama.cpp` has first-class ARM/NEON support, making it the practical
choice for CPU-only and Pi deployment.
