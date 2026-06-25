"""Retriever interfaces and PostgreSQL-backed strategy placeholders."""

from .retriever import (
    BaseRetriever,
    HybridRetriever,
    SearchResult,
    TextRetriever,
    VectorRetriever,
)

__all__ = [
    "BaseRetriever",
    "HybridRetriever",
    "SearchResult",
    "TextRetriever",
    "VectorRetriever",
]
