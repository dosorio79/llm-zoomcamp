from sqlitesearch import TextSearchIndex

# Database configuration parameters
DB_PATH = "storage/chunk.db"

def open_index() -> TextSearchIndex:
    """Initialize and return a TextSearchIndex instance for text search."""
    return TextSearchIndex(
        text_fields=["content"],
        keyword_fields=["filename"],
        db_path=str(DB_PATH),
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
