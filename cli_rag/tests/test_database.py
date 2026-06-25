import unittest
from unittest.mock import patch


class DatabaseImportTests(unittest.TestCase):
    def test_import_does_not_open_a_database_connection(self) -> None:
        with patch("psycopg.connect") as connect:
            from src.db import schema

            self.assertTrue(callable(schema.setup_schema))

        connect.assert_not_called()


if __name__ == "__main__":
    unittest.main()
