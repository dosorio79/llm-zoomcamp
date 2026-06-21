from sqlitesearch import TextSearchIndex

from .config import INDEX_KEYWORD_FIELDS, INDEX_TEXT_FIELDS, TEXT_DB_PATH


def open_index() -> TextSearchIndex:
    """Initialize and return a TextSearchIndex instance for text search."""
    return TextSearchIndex(
        text_fields=INDEX_TEXT_FIELDS,
        keyword_fields=INDEX_KEYWORD_FIELDS,
        db_path=str(TEXT_DB_PATH),
    )


_index = None


def get_index() -> TextSearchIndex:
    """Get or initialize the global text search index."""
    global _index

    if _index is None:
        _index = open_index()

    return _index


def search(
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

    index = get_index()

    return index.search(
        query=query,
        num_results=max(1, top_k),
    )
