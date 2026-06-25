"""Retriever interfaces for the shared PostgreSQL search backend."""

from abc import ABC, abstractmethod
from typing import TypedDict

from ..config import DATABASE_URL


class SearchResult(TypedDict):
    """Normalized result returned by every retrieval strategy."""

    id: int
    filename: str
    start: int
    content: str
    score: float


class BaseRetriever(ABC):
    """Common lazy database configuration and search contract."""

    def __init__(self, database_url: str = DATABASE_URL) -> None:
        self.database_url = database_url

    def search(self, query: str, top_k: int = 5) -> list[SearchResult]:
        if not query or not query.strip():
            return []

        return self._search(query=query, top_k=max(1, top_k))

    @abstractmethod
    def _search(self, query: str, top_k: int) -> list[SearchResult]:
        """Execute a retrieval strategy for a non-empty query."""


class TextRetriever(BaseRetriever):
    """Retrieve chunks with pg_textsearch BM25 ranking."""

    def _search(self, query: str, top_k: int) -> list[SearchResult]:
        raise NotImplementedError("BM25 retrieval SQL is not implemented yet.")


class VectorRetriever(BaseRetriever):
    """Retrieve chunks with pgvector cosine similarity."""

    def _search(self, query: str, top_k: int) -> list[SearchResult]:
        raise NotImplementedError(
            "Query embedding and vector retrieval SQL are not implemented yet."
        )


class HybridRetriever(BaseRetriever):
    """Fuse results from the text and vector retrieval strategies."""

    def __init__(
        self,
        database_url: str = DATABASE_URL,
        text_retriever: TextRetriever | None = None,
        vector_retriever: VectorRetriever | None = None,
    ) -> None:
        super().__init__(database_url=database_url)
        self.text_retriever = text_retriever or TextRetriever(database_url)
        self.vector_retriever = vector_retriever or VectorRetriever(database_url)

    def _search(self, query: str, top_k: int) -> list[SearchResult]:
        raise NotImplementedError("Hybrid result fusion is not implemented yet.")
