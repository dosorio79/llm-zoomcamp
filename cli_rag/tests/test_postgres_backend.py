import unittest
from unittest.mock import patch


class PostgresBackendImportTests(unittest.TestCase):
    def test_import_does_not_open_a_database_connection(self) -> None:
        with patch("psycopg.connect") as connect:
            from src_new.indexing import postgres_backend

            self.assertTrue(callable(postgres_backend.setup_schema))

        connect.assert_not_called()


if __name__ == "__main__":
    unittest.main()
