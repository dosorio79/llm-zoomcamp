from typing import Any, Callable, List
import os
from sqlitesearch import TextSearchIndex
from ..config import INDEX_KEYWORD_FIELDS, INDEX_TEXT_FIELDS, TEXT_DB_PATH


def build_index(
    chunks: List[Any],
    text_fields: List[str] = INDEX_TEXT_FIELDS,
    keyword_fields: List[str] = INDEX_KEYWORD_FIELDS,
    db_path: str = TEXT_DB_PATH,
    progress_callback: Callable[..., None] | None = None,
) -> Any:
    """
    Create and fit an Index with the provided documents.
    
    Args:
        chunks: List of document chunks to fit the index with.
        text_fields: List of field names to use as text fields in the index.
        keyword_fields: List of field names to use as keyword fields in the index.
        db_path: Path to the database file for storing the index.
    
    Returns:
        Any: The fitted Index object.
    """
    db_dir = os.path.dirname(db_path)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

    index = TextSearchIndex(
        text_fields=text_fields,
        keyword_fields=keyword_fields,
        db_path=db_path)
    
    for doc in chunks:
        index.add(doc)
        if progress_callback:
            progress_callback()
    
    index.close()
    return index
