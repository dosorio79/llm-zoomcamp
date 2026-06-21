"""
TextRetriever class for retrieving relevant text documents based on a query.
"""
from sqlitesearch import TextSearchIndex

from .. import config

# Database configuration parameters
DB_PATH = config.TEXT_DB_PATH

class TextRetriever:
    """
    A class to retrieve relevant text documents from a SQLite database using full-text search.
    """

    def __init__(self):
        """Initialize the TextRetriever with a TextSearchIndex instance."""
        self.index = self.open_index()

    def open_index(self) -> TextSearchIndex:
        """Initialize and return a TextSearchIndex instance for text search."""
        return TextSearchIndex(
            text_fields=["content"],
            keyword_fields=["filename"],
            db_path=str(DB_PATH),
        )

    def search(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[dict]:
        """
        Search the index for documents matching the query.

        Args:
            query: Search query string.
            top_k: Maximum number of results to return.

        Returns:
            List of matching documents with metadata.
        """
        if not query or not query.strip():
            return []

        return self.index.search(
            query=query,
            num_results=max(1, top_k),
        )

