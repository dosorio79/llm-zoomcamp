"""PostgreSQL connection helpers."""

import psycopg
from psycopg import Connection

from ..config import DATABASE_URL


def connect(database_url: str = DATABASE_URL) -> Connection:
    """Open a PostgreSQL connection when a database operation is requested."""
    return psycopg.connect(database_url)
