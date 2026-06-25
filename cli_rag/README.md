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

You can also keep a shared `.env` in the repository root or in `Lessons/.env`.
The CLI loads `cli_rag/.env` first, then falls back to `../.env` and
`../Lessons/.env` without overriding variables already exported in your shell.

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

## PostgreSQL backend scaffold

The in-progress `src_new` package uses a shared PostgreSQL table for BM25 and
vector search. Build and start PostgreSQL 17 with `pg_textsearch` and `pgvector`:

```bash
make db-build
make db-start
make schema-setup
```

The schema setup is idempotent. To recreate only the application schema:

```bash
make schema-reset
```

To remove the development container and its data volume:

```bash
make db-reset
```

Connection settings default to the values in `.env.example` and can be
overridden with `DATABASE_URL` and `DATABASE_SCHEMA`.
