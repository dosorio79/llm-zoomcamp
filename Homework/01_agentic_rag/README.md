# Agentic RAG Homework

Homework implementation for LLM Zoomcamp module 1. The repository has two
parts:

- the homework/checker work, centered on `notebooks/gitrag.ipynb` and
  `src/rag_helper.py`
- a standalone terminal demo, centered on `main.py` and the remaining modules
  under `src/`

Both parts use the LLM Zoomcamp lesson markdown files as the knowledge base,
pinned to commit `8c1834d` from `DataTalksClub/llm-zoomcamp`.

## Setup

Install dependencies with `uv`:

```bash
uv sync
```

Create a local environment file:

```bash
cp .env.example .env
```

Then set:

```bash
OPENAI_API_KEY=...
```

The code uses OpenAI Responses API calls with `gpt-5.4-mini` by default.

## Homework Files

These files are the important ones for homework answers and checks:

- `notebooks/gitrag.ipynb`: notebook used to work through the questions
- `src/rag_helper.py`: adapted RAG helper used by the notebook/check flow
- `docs/answers.example.md`: blank answer template for local use
- `HOMEWORK.md`: original homework prompt

`src/rag_helper.py` is intentionally separate from the standalone demo code.
It keeps the helper-style implementation expected by the homework flow:

- receives an existing search index and LLM client
- searches lesson documents by `filename` and `content`
- builds the prompt context
- returns both the answer text and token usage

To keep selected answers out of git, copy the example template when you want a
local answer sheet:

```bash
cp docs/answers.example.md docs/answers.md
```

## Standalone Demo

The standalone demo is an interactive CLI that can build the local index and
run either plain RAG or agentic RAG.

Run it with:

```bash
make run
```

The menu offers:

- `Build / rebuild index`: fetch lesson markdown, chunk it, and write the
  SQLite search index
- `Plain RAG`: retrieve once, build a context prompt, and answer
- `Agentic RAG`: give the model a `search` tool and let it decide when to use it
- `Exit`: close the CLI

Inside either chat loop, enter `exit`, `quit`, or `stop` to return to the menu.

The generated index is stored at:

```text
storage/chunk.db
```

It is created on first use if missing.

## Demo Module Map

The standalone demo uses these modules:

- `main.py`: Rich terminal UI, index setup, and chat loop selection
- `src/ingestion.py`: downloads lesson markdown, chunks documents, and builds
  the SQLite search index
- `src/retrival.py`: opens `storage/chunk.db` and performs search
- `src/rag.py`: plain RAG assistant
- `src/agent.py`: ToyAIKit/OpenAI agent runner
- `src/tools.py`: registers the search tool for the agent
- `src/prompts.py`: shared prompts for plain RAG and agentic RAG

Note: `src/retrival.py` keeps its current filename to avoid changing imports.

## Data Flow

For the demo index:

1. `src/ingestion.py` fetches markdown lesson files from GitHub.
2. Documents are chunked with `size=2000` and `step=1000`.
3. Chunks are indexed into `storage/chunk.db` with `sqlitesearch`.
4. Plain RAG calls search once and sends the retrieved context to the model.
5. Agentic RAG exposes search as a tool and lets the model make tool calls
   before producing the final answer.

## Useful Commands

Compile-check the Python files:

```bash
uv run python -m py_compile main.py src/*.py
```

Run the standalone demo:

```bash
make run
```

Open the notebook with your preferred Jupyter environment and run
`notebooks/gitrag.ipynb` for the homework workflow.
