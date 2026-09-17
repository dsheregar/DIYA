#!/usr/bin/env python3
"""List Hugging Face models fine-tuned from a given base model.

Used to find merge candidates that share the same architecture and
tokenizer as DIYA's base model, since mergekit requires that.

Usage:
    python find_compatible_models.py meta-llama/Llama-3.2-3B-Instruct
"""
import sys

import requests

API_URL = "https://huggingface.co/api/models"


def find_compatible(base_model: str, limit: int = 30):
    resp = requests.get(
        API_URL,
        params={"filter": f"base_model:{base_model}", "limit": limit, "sort": "downloads", "direction": -1},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)

    base_model = sys.argv[1]
    models = find_compatible(base_model)
    if not models:
        print(f"No models found tagged as derived from {base_model}.")
        return

    print(f"Models derived from {base_model}:\n")
    for m in models:
        print(f"  {m['id']}  (downloads: {m.get('downloads', '?')})")


if __name__ == "__main__":
    main()
