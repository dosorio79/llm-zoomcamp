"""PostgreSQL schema management for the shared search backend."""

import argparse
from collections.abc import Sequence

from psycopg import sql

from ..config import (
    BM25_INDEX_NAME,
    CHUNKS_TABLE,
    DATABASE_SCHEMA,
    DATABASE_URL,
    EMBEDDING_DIMENSION,
    VECTOR_INDEX_NAME,
)
from .connection import connect


def schema_statements() -> Sequence[sql.SQL | sql.Composed]:
    """Return the idempotent DDL statements for the shared chunks backend."""
    schema = sql.Identifier(DATABASE_SCHEMA)
    table = sql.Identifier(CHUNKS_TABLE)

    return (
        sql.SQL("CREATE EXTENSION IF NOT EXISTS vector"),
        sql.SQL("CREATE EXTENSION IF NOT EXISTS pg_textsearch"),
        sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(schema),
        sql.SQL(
            """
            CREATE TABLE IF NOT EXISTS {}.{} (
                id BIGSERIAL PRIMARY KEY,
                filename TEXT NOT NULL,
                start INTEGER NOT NULL,
                content TEXT NOT NULL,
                embedding vector({}),
                UNIQUE (filename, start)
            )
            """
        ).format(
            schema,
            table,
            sql.Literal(EMBEDDING_DIMENSION),
        ),
        sql.SQL(
            """
            CREATE INDEX IF NOT EXISTS {} ON {}.{}
            USING bm25 (content)
            WITH (text_config = 'english')
            """
        ).format(
            sql.Identifier(BM25_INDEX_NAME),
            schema,
            table,
        ),
        sql.SQL(
            """
            CREATE INDEX IF NOT EXISTS {} ON {}.{}
            USING hnsw (embedding vector_cosine_ops)
            """
        ).format(
            sql.Identifier(VECTOR_INDEX_NAME),
            schema,
            table,
        ),
    )


def setup_schema(database_url: str = DATABASE_URL) -> None:
    """Create extensions, the chunks table, and both search indexes."""
    with connect(database_url) as connection:
        with connection.cursor() as cursor:
            for statement in schema_statements():
                cursor.execute(statement)


def reset_schema(database_url: str = DATABASE_URL) -> None:
    """Drop the application schema and recreate an empty search backend."""
    with connect(database_url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                sql.SQL("DROP SCHEMA IF EXISTS {} CASCADE").format(
                    sql.Identifier(DATABASE_SCHEMA)
                )
            )

    setup_schema(database_url)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("setup", "reset"))
    args = parser.parse_args()

    if args.action == "reset":
        reset_schema()
    else:
        setup_schema()


if __name__ == "__main__":
    main()
