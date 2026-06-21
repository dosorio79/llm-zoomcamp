"""Vector retriever placeholder."""

from typing import Any


class VectorRetriever:
    """Retrieve documents from a vector index."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        raise NotImplementedError("Vector retriever is not implemented yet.")

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """Search for documents matching the query."""
        raise NotImplementedError("Vector search is not implemented yet.")
