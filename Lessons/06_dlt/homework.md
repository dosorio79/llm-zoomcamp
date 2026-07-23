# Homework: dlt

## Overview

In this homework, the Module 1 FAQ agent is:

- Rewritten using Pydantic AI
- Instrumented with Pydantic Logfire
- Exported with dlt
- Stored and analyzed in DuckDB

---

# Setup

## Download the homework files

```bash
PREFIX=https://raw.githubusercontent.com/DataTalksClub/llm-zoomcamp/main/cohorts/2026/workshops/dlt/homework

wget $PREFIX/agent.py
wget $PREFIX/ingest.py
wget $PREFIX/main.py
wget $PREFIX/.env.example -O .env
```

## Initialize the project

```bash
uv init
uv add openai minsearch requests python-dotenv pydantic-ai logfire
uv add "dlt[duckdb]"
```

## Configure environment variables

Add your OpenAI API key to `.env`:

```env
OPENAI_API_KEY=sk-YOUR_KEY_HERE
```

Make sure `.env` is in `.gitignore`:

```text
.env
```

## Verify the agent

```bash
uv run python main.py
```

---

# Question 1 - Instrument the agent with Logfire

Create a free Logfire account, create a project, and generate a write token.

Add the token to `.env`:

```env
LOGFIRE_TOKEN=YOUR_LOGFIRE_WRITE_TOKEN
```

Instrument the agent:

```python
logfire.configure()
logfire.instrument_pydantic_ai()
```

Run the agent several times using different questions and inspect the traces in Logfire.

For the following query:

> **How do I run Ollama locally?**

How many spans does a single agent run produce?

Each span is either:

- the agent run itself
- an LLM call
- a tool call

The number can vary between runs because the model decides how many times to search.

## Options

- [ ] 1
- [x] 5
- [ ] 15
- [ ] 30

## Answer

**Selected option:**

**Observed number of spans:**
5 spans (3 llm and 2 tool calls)
## Notes

---

# Question 2 - Load traces into DuckDB with dlt

Generate a read token for the Logfire project and add it to `.env`:

```env
LOGFIRE_READ_TOKEN=YOUR_LOGFIRE_READ_TOKEN
```

Initialize a dltHub project as shown in the workshop.

Use the Logfire source context:

https://dlthub.com/context/source/logfire

Pull the Logfire traces into DuckDB.

The Logfire traces contain deeply nested JSON. dlt automatically normalizes this into a main table and multiple child tables.

Run:

```sql
SELECT COUNT(*)
FROM information_schema.tables
WHERE table_schema = 'agent_traces';
```

How many tables did dlt create?

## Options

- [ ] 1
- [ ] 3
- [x] 24
- [ ] 100

## Answer

**Selected option:**

**Observed number of tables:**

## Validation SQL

```sql
-- Additional queries if needed
```

## Notes

---

# Question 3 - Query traces with an agent

Using a coding agent (or manually), find the input token usage for the same agent run from Question 1.

The token counts are stored as:

```text
gen_ai.usage.input_tokens
```

Sum the input tokens across all LLM calls within the trace.

Because the number of searches varies, report the range that contains the total.

## Options

- [ ] 100–500
- [x] 1,500–5,000
- [ ] 10,000–20,000
- [ ] 50,000–100,000

## Answer

**Selected range:**

**Calculated input token total:**

## SQL / Calculation

```sql
-- Paste the query used here
```

## Notes

---

# Final Answers

| Question | Selected Answer | Observed Value |
|----------|-----------------|---------------:|
| Question 1 | | |
| Question 2 | | |
| Question 3 | | |

---

# Submission

https://courses.datatalks.club/llm-zoomcamp-2026/homework/dlt