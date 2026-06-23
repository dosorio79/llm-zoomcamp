import os
from collections.abc import Callable
from typing import List, Any

from sqlitesearch import TextSearchIndex
from gitsource import GithubRepositoryDataReader, chunk_documents 

# Repository configuration parameters
REPO_OWNER = "DataTalksClub"
REPO_NAME = "llm-zoomcamp"
COMMIT_ID = "8c1834d"
ALLOWED_EXTENSIONS = {"md"}

# Index configuration parameters
INDEX_TEXT_FIELDS = ["content"]
INDEX_KEYWORD_FIELDS = ["filename"]

# Chunking configuration parameters
CHUNK_SIZE = 2000
CHUNK_STEP = 1000

# Database configuration parameters
DB_PATH = "storage/chunk.db"

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

def chunk_documents_for_indexing(documents: List[Any]) -> List[Any]:
    chunks = chunk_documents(documents, size=CHUNK_SIZE, step=CHUNK_STEP)
    return chunks


def build_index(
    chunks: List[Any],
    text_fields: List[str] = INDEX_TEXT_FIELDS,
    keyword_fields: List[str] = INDEX_KEYWORD_FIELDS,
    db_path: str = DB_PATH,
    progress_callback: Callable[[], None] | None = None,
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
        # for rich progress reporting, we can call the progress_callback after each document is added
        if progress_callback:
            progress_callback()
    
    index.close()
    return index
