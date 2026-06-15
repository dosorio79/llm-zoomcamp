# LLM Zoomcamp RAG Assistant

A Retrieval-Augmented Generation (RAG) assistant for answering questions about [DataTalks.club](https://datatalks.club/) courses. It fetches FAQ data from the DataTalks.club API, builds a search index, and uses an OpenAI LLM to answer natural-language questions grounded in that content.

## How it works

1. **Ingestion** — FAQ documents are fetched from the DataTalks.club API and indexed with [`minsearch`](https://github.com/alexeygrigorev/minsearch).
2. **Retrieval** — User queries are searched against the index, boosting the `question` field and filtering by course.
3. **Generation** — The top results are formatted into a prompt and sent to an OpenAI model, which returns a grounded answer.

## Project structure

```
.
├── .env.example      # Shared environment variable template
├── pyproject.toml    # Shared project metadata and dependencies
├── uv.lock           # Shared lockfile
└── 01_agentic_rag/
    ├── ingestion.py  # Fetches FAQ data and builds the search index
    ├── main.py       # Entry point: wires everything together and runs the CLI
    ├── prompts.py    # System instructions and user prompt template
    ├── rag_helper.py # RAGBase class encapsulating search, prompt building, and LLM calls
    └── notebooks/    # Exploratory notebooks
```

## Requirements

- Python ≥ 3.14
- An OpenAI API key

## Setup

```bash
# Install dependencies (recommended: uv)
uv sync

# Copy and fill in your API key
echo "OPENAI_API_KEY=sk-..." > .env
```

## Usage

```bash
uv run python 01_agentic_rag/main.py
```

You will be prompted to enter a question. The assistant searches the FAQ index and returns an answer.

```
Please enter your question: How do I get a certificate?
```

## Configuration

`RAGBase` accepts the following parameters (all have defaults):

| Parameter              | Default                  | Description                          |
|------------------------|--------------------------|--------------------------------------|
| `index`                | —                        | Fitted `minsearch` index             |
| `llm_client`           | —                        | OpenAI client instance               |
| `instructions`         | See `prompts.py`         | System prompt for the LLM            |
| `user_prompt_template` | See `prompts.py`         | Template used to format user prompts |
| `course`               | `"llm-zoomcamp"`         | Course to filter search results by   |
| `model`                | `"gpt-5.4-mini"`         | OpenAI model to use                  |

## Dependencies

| Package          | Purpose                        |
|------------------|--------------------------------|
| `openai`         | LLM API client                 |
| `minsearch`      | Lightweight in-memory search   |
| `requests`       | Fetching FAQ data from the API |
| `python-dotenv`  | Loading `.env` for API keys    |
