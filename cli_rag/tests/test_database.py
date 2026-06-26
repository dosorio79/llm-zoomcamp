import unittest
from unittest.mock import MagicMock, patch

from src.db.connection import execute, fetch_all


class DatabaseImportTests(unittest.TestCase):
    def test_import_does_not_open_a_database_connection(self) -> None:
        with patch("psycopg.connect") as connect:
            from src.db import schema

            self.assertTrue(callable(schema.setup_schema))

        connect.assert_not_called()


class DatabaseQueryHelperTests(unittest.TestCase):
    @patch("src.db.connection.connect")
    def test_fetch_all_returns_query_rows(self, connect: MagicMock) -> None:
        cursor = connect.return_value.__enter__.return_value.cursor.return_value
        cursor.__enter__.return_value.fetchall.return_value = [(1, "first")]

        rows = fetch_all(
            "SELECT id, content FROM rag.chunks WHERE filename = %s",
            ("lesson.md",),
            database_url="postgresql://test",
        )

        self.assertEqual(rows, [(1, "first")])
        connect.assert_called_once_with("postgresql://test")
        cursor.__enter__.return_value.execute.assert_called_once_with(
            "SELECT id, content FROM rag.chunks WHERE filename = %s",
            ("lesson.md",),
        )

    @patch("src.db.connection.connect")
    def test_execute_returns_affected_row_count(self, connect: MagicMock) -> None:
        cursor = connect.return_value.__enter__.return_value.cursor.return_value
        cursor.__enter__.return_value.rowcount = 3

        affected = execute(
            "DELETE FROM rag.chunks WHERE filename = %s",
            ("lesson.md",),
            database_url="postgresql://test",
        )

        self.assertEqual(affected, 3)
        connect.assert_called_once_with("postgresql://test")
        cursor.__enter__.return_value.execute.assert_called_once_with(
            "DELETE FROM rag.chunks WHERE filename = %s",
            ("lesson.md",),
        )


if __name__ == "__main__":
    unittest.main()
