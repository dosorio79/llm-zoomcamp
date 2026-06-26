"""Database connection and schema management."""


def setup_schema(database_url: str | None = None) -> None:
    """Create the shared PostgreSQL search schema."""
    from .schema import setup_schema as setup

    if database_url is None:
        setup()
    else:
        setup(database_url)


def reset_schema(database_url: str | None = None) -> None:
    """Drop and recreate the shared PostgreSQL search schema."""
    from .schema import reset_schema as reset

    if database_url is None:
        reset()
    else:
        reset(database_url)

__all__ = ["reset_schema", "setup_schema"]
