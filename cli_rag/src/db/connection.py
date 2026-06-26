"""PostgreSQL connection helpers."""

import psycopg
from psycopg import Connection
from psycopg.abc import Params, QueryNoTemplate
from psycopg.rows import TupleRow

from ..config import DATABASE_URL


def connect(database_url: str = DATABASE_URL) -> Connection:
    """Open a PostgreSQL connection when a database operation is requested."""
    return psycopg.connect(database_url)


def fetch_all(
    query: QueryNoTemplate,
    params: Params | None = None,
    *,
    database_url: str = DATABASE_URL,
) -> list[TupleRow]:
    """Execute a read query and return all rows."""
    with connect(database_url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()


def execute(
    query: QueryNoTemplate,
    params: Params | None = None,
    *,
    database_url: str = DATABASE_URL,
) -> int:
    """Execute a write query and return the number of affected rows."""
    with connect(database_url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.rowcount
