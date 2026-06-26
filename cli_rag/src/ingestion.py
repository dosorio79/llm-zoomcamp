"""Load, chunk, embed, and persist repository documents."""

from collections.abc import Mapping, Sequence
from typing import Any, Protocol

import numpy as np
from gitsource import GithubRepositoryDataReader, chunk_documents
from pgvector.psycopg import register_vector
from psycopg import sql

from .config import (
    ALLOWED_EXTENSIONS,
    CHUNK_SIZE,
    CHUNK_STEP,
    CHUNKS_TABLE,
    COMMIT_ID,
    DATABASE_SCHEMA,
    DATABASE_URL,
    EMBEDDING_DIMENSION,
    REPO_NAME,
    REPO_OWNER,
)
from .db.connection import connect
from .embed import Embedder


DEFAULT_INSERT_BATCH_SIZE = 64


class BatchEmbedder(Protocol):
    """Minimal embedding interface required by the ingestion pipeline."""

    def encode_batch(
        self, texts: Sequence[str], normalize: bool = True
    ) -> np.ndarray: ...


def load_documents_from_repo():
    reader = GithubRepositoryDataReader(
        repo_owner=REPO_OWNER,
        repo_name=REPO_NAME,
        commit_id=COMMIT_ID,
        allowed_extensions=ALLOWED_EXTENSIONS,
        filename_filter=lambda path: "/lessons/" in path,
    )
    files = reader.read()

    documents = []
    for file in files:
        doc = file.parse()
        documents.append(doc)
    return documents


def chunk_documents_for_indexing(documents: list[Any]) -> list[Any]:
    chunks = chunk_documents(documents, size=CHUNK_SIZE, step=CHUNK_STEP)
    return chunks


def _chunk_values(chunk: Mapping[str, Any]) -> tuple[str, int, str]:
    """Validate and return the fields stored by the chunks table."""
    try:
        filename = chunk["filename"]
        start = chunk["start"]
        content = chunk["content"]
    except KeyError as error:
        raise ValueError(f"Chunk is missing required field: {error.args[0]}") from error

    if not isinstance(filename, str) or not filename:
        raise ValueError("Chunk field 'filename' must be a non-empty string")
    if not isinstance(start, int) or isinstance(start, bool) or start < 0:
        raise ValueError("Chunk field 'start' must be a non-negative integer")
    if not isinstance(content, str) or not content:
        raise ValueError("Chunk field 'content' must be a non-empty string")

    return filename, start, content


def insert_chunks(
    chunks: Sequence[Mapping[str, Any]],
    *,
    database_url: str = DATABASE_URL,
    embedder: BatchEmbedder | None = None,
    batch_size: int = DEFAULT_INSERT_BATCH_SIZE,
) -> int:
    """Embed chunks and upsert them into PostgreSQL.

    Existing rows with the same ``(filename, start)`` are refreshed, which makes
    rerunning ingestion safe.
    """
    if batch_size < 1:
        raise ValueError("batch_size must be at least 1")
    if not chunks:
        return 0

    validated_chunks = [_chunk_values(chunk) for chunk in chunks]

    if embedder is None:
        embedder = Embedder()

    insert_statement = sql.SQL(
        """
        INSERT INTO {}.{} (filename, start, content, embedding)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (filename, start) DO UPDATE SET
            content = EXCLUDED.content,
            embedding = EXCLUDED.embedding
        """
    ).format(
        sql.Identifier(DATABASE_SCHEMA),
        sql.Identifier(CHUNKS_TABLE),
    )

    inserted = 0
    with connect(database_url) as connection:
        register_vector(connection)
        with connection.cursor() as cursor:
            for offset in range(0, len(validated_chunks), batch_size):
                values = validated_chunks[offset : offset + batch_size]
                embeddings = np.asarray(
                    embedder.encode_batch([content for _, _, content in values]),
                    dtype=np.float32,
                )

                expected_shape = (len(values), EMBEDDING_DIMENSION)
                if embeddings.shape != expected_shape:
                    raise ValueError(
                        "Embedder returned shape "
                        f"{embeddings.shape}; expected {expected_shape}"
                    )

                rows = [
                    (filename, start, content, embedding)
                    for (filename, start, content), embedding in zip(
                        values, embeddings, strict=True
                    )
                ]
                cursor.executemany(insert_statement, rows)
                inserted += len(rows)

    return inserted


def ingest_repository(
    *,
    database_url: str = DATABASE_URL,
    embedder: BatchEmbedder | None = None,
    batch_size: int = DEFAULT_INSERT_BATCH_SIZE,
) -> int:
    """Run the complete repository ingestion workflow."""
    documents = load_documents_from_repo()
    chunks = chunk_documents_for_indexing(documents)
    return insert_chunks(
        chunks,
        database_url=database_url,
        embedder=embedder,
        batch_size=batch_size,
    )


def main() -> None:
    inserted = ingest_repository()
    print(f"Ingested {inserted} chunks.")


if __name__ == "__main__":
    main()
