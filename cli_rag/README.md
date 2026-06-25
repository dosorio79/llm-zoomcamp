# CLI RAG

Standalone terminal RAG app based on Homework 01. The current implementation is
being migrated to one PostgreSQL backend for BM25, vector, and hybrid retrieval.

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

## PostgreSQL backend

The `src/db` package manages PostgreSQL connections and schema setup. The
`src/retrieval` package contains the shared retriever contract and text, vector,
and hybrid strategies. Build and start PostgreSQL 17 with `pg_textsearch` and
`pgvector`:

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

## Run

Start the CLI:

```bash
make run
```

The menu provides schema setup/reset and plain or agentic RAG entry points.
Chunk insertion and retriever search SQL remain explicit placeholders while the
PostgreSQL migration is in progress.
