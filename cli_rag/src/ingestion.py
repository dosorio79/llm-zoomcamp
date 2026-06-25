from typing import Any

from gitsource import GithubRepositoryDataReader, chunk_documents

from .config import (
    ALLOWED_EXTENSIONS,
    CHUNK_SIZE,
    CHUNK_STEP,
    COMMIT_ID,
    REPO_NAME,
    REPO_OWNER,
)


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
