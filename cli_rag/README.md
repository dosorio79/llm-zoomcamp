# CLI RAG

Standalone terminal RAG app based on Homework 01.

It can build a local lesson index and run either plain RAG or agentic RAG over
the LLM Zoomcamp lesson markdown files.

## Setup

Install dependencies:

```bash
uv sync
```

Create a local environment file:

```bash
cp .env.example .env
```

Set your OpenAI API key:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

## Run

Start the CLI:

```bash
make run
```

The menu includes:

- `Build / rebuild index`: fetch lesson markdown, chunk it, and write the local
  SQLite search index
- `Clean index`: remove the local SQLite search index
- `Plain RAG`: retrieve once and answer with retrieved context
- `Agentic RAG`: expose search as a tool and let the model decide when to use it
- `Exit`: close the CLI

Inside a chat loop, type `exit`, `quit`, or `stop` to return to the menu.

The generated index is stored at:

```text
storage/chunk.db
```
