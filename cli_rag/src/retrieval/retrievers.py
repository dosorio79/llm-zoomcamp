"""Retriever interfaces for the shared PostgreSQL search backend."""

from typing import Any, TypedDict

import numpy as np
from pgvector.psycopg import register_vector
from psycopg import sql

from ..config import BM25_INDEX_NAME, CHUNKS_TABLE, DATABASE_SCHEMA, DATABASE_URL
from ..db.connection import connect, fetch_all
from ..embed import Embedder


class SearchResult(TypedDict):
    """Normalized result returned by every retrieval strategy."""

    id: int
    filename: str
    start: int
    content: str
    score: float


def rows_to_results(rows) -> list[SearchResult]:
    return [
        {
            "id": row[0],
            "filename": row[1],
            "start": row[2],
            "content": row[3],
            "score": float(row[4]),
        }
        for row in rows
    ]


def bm25_index_name() -> str:
    return f"{DATABASE_SCHEMA}.{BM25_INDEX_NAME}"


class BaseRetriever:
    """Common database configuration and search validation."""

    def __init__(self, database_url: str = DATABASE_URL) -> None:
        self.database_url = database_url

    def search(self, query: str, top_k: int = 5) -> list[SearchResult]:
        if not query or not query.strip():
            return []

        return self._search(query=query, top_k=max(1, top_k))

    def _search(self, query: str, top_k: int) -> list[SearchResult]:
        raise NotImplementedError


class TextRetriever(BaseRetriever):
    """Retrieve chunks with PostgreSQL full-text ranking."""

    def _search(self, query: str, top_k: int) -> list[SearchResult]:
        statement = sql.SQL(
            """
            SELECT
                id,
                filename,
                start,
                content,
                -(content <@> to_bm25query(%s, %s)) AS score
            FROM {}.{}
            ORDER BY content <@> to_bm25query(%s, %s), id
            LIMIT %s
            """
        ).format(
            sql.Identifier(DATABASE_SCHEMA),
            sql.Identifier(CHUNKS_TABLE),
        )

        return rows_to_results(
            fetch_all(
                statement,
                (query, bm25_index_name(), query, bm25_index_name(), top_k),
                database_url=self.database_url,
            )
        )


class VectorRetriever(BaseRetriever):
    """Retrieve chunks with pgvector cosine similarity."""

    def __init__(
        self,
        database_url: str = DATABASE_URL,
        embedder: Any | None = None,
    ) -> None:
        super().__init__(database_url=database_url)
        self.embedder = embedder

    def _search(self, query: str, top_k: int) -> list[SearchResult]:
        embedder = self.embedder or Embedder()
        query_vector = np.asarray(embedder.encode(query), dtype=np.float32)

        statement = sql.SQL(
            """
            SELECT
                id,
                filename,
                start,
                content,
                1 - (embedding <=> %s::vector) AS score
            FROM {}.{}
            WHERE embedding IS NOT NULL
            ORDER BY embedding <=> %s::vector, id
            LIMIT %s
            """
        ).format(
            sql.Identifier(DATABASE_SCHEMA),
            sql.Identifier(CHUNKS_TABLE),
        )

        with connect(self.database_url) as connection:
            register_vector(connection)
            with connection.cursor() as cursor:
                cursor.execute(statement, (query_vector, query_vector, top_k))
                return rows_to_results(cursor.fetchall())


class HybridRetriever(BaseRetriever):
    """Combine text and vector results with reciprocal-rank fusion."""

    def __init__(
        self,
        database_url: str = DATABASE_URL,
        text_retriever: Any | None = None,
        vector_retriever: Any | None = None,
    ) -> None:
        super().__init__(database_url=database_url)
        self.text_retriever = text_retriever or TextRetriever(database_url)
        self.vector_retriever = vector_retriever or VectorRetriever(database_url)

    def _search(self, query: str, top_k: int) -> list[SearchResult]:
        candidates: dict[int, SearchResult] = {}

        for results in (
            self.text_retriever.search(query, top_k=top_k),
            self.vector_retriever.search(query, top_k=top_k),
        ):
            for rank, result in enumerate(results, start=1):
                document_id = result["id"]
                if document_id not in candidates:
                    candidates[document_id] = {**result, "score": 0.0}

                candidates[document_id]["score"] += 1 / rank

        return sorted(
            candidates.values(),
            key=lambda result: result["score"],
            reverse=True,
        )[:top_k]
