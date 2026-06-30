import os
from pathlib import Path


# Repository configuration parameters
REPO_OWNER = "DataTalksClub"
REPO_NAME = "llm-zoomcamp"
COMMIT_ID = "8c1834d"
ALLOWED_EXTENSIONS = {"md"}

# Chunking configuration parameters
CHUNK_SIZE = 2000
CHUNK_STEP = 1000

# Database configuration parameters
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/cli_rag",
)
DATABASE_SCHEMA = os.getenv("DATABASE_SCHEMA", "rag")
CHUNKS_TABLE = "chunks"
EMBEDDING_DIMENSION = 384
BM25_INDEX_NAME = "chunks_content_bm25_idx"
VECTOR_INDEX_NAME = "chunks_embedding_hnsw_idx"

# Reranking configuration parameters
RERANKER_MODEL_REPO = "Xenova/ms-marco-MiniLM-L-6-v2"
RERANKER_MODEL_PATH = os.getenv(
    "RERANKER_MODEL_PATH",
    str(
        Path(__file__).resolve().parent
        / "rerank"
        / "models"
        / RERANKER_MODEL_REPO
    ),
)
