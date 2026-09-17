# merge/

Config and steps for producing DIYA's merged base model.

## 1. Find compatible fine-tunes

```bash
python ../scripts/find_compatible_models.py meta-llama/Llama-3.2-3B-Instruct
```

This lists Hugging Face models tagged as derived from that base model.
Pick 1-3 that add something useful (e.g. a coding-focused tune, a
reasoning-focused tune) and note their exact repo IDs.

## 2. Fill in `mergekit_config.yaml`

Replace the commented-out placeholder entries with the real model IDs
you picked, and tune the `weight`/`density` parameters (start at equal
weights and adjust after testing).

## 3. Run the merge

```bash
pip install mergekit
mergekit-yaml mergekit_config.yaml ../merged-model
```

This downloads each listed model's full-precision weights (multi-GB
each) and writes the merged result to `../merged-model/`. That folder
is git-ignored — it's a local build artifact, not something to commit.

## 4. Convert to GGUF and quantize

Use `llama.cpp`'s conversion script against `../merged-model/`, then
quantize (Q4_K_M is a good starting point for CPU/Pi use). See
[`../docs/ROADMAP.md`](../docs/ROADMAP.md) Phase 3.
