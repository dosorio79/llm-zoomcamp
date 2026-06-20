# LLM Zoomcamp Homework 2: Vector Search

This directory contains my working code for the LLM Zoomcamp 2026 Module 2
homework on vector search.

The work explores embedding lesson documents, comparing cosine similarity,
running keyword and vector search with `minsearch`, and combining results with
reciprocal rank fusion.

## Contents

- `embedder.py` - small ONNX-based sentence embedding helper.
- `download.py` - downloads the tokenizer and ONNX model from Hugging Face.
- `notebooks/gitrag_vector.ipynb` - notebook used to compute and inspect the
  homework results.
- `pyproject.toml` / `uv.lock` - Python dependencies managed with `uv`.


## Setup

Install dependencies:

```bash
uv sync
```

Download the local embedding model:

```bash
uv run python download.py
```

This stores model files under `models/`, which is ignored because the files are
downloadable artifacts.

## Run

Open the notebook:

```bash
uv run jupyter lab notebooks/gitrag_vector.ipynb
```

The notebook expects the downloaded model at:

```text
models/Xenova/all-MiniLM-L6-v2
```

## Notes

The embedder returns normalized vectors, so dot products can be used directly as
cosine similarities.
