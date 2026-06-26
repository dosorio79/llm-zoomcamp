import unittest
from unittest.mock import Mock, call, patch

import numpy as np

from src.config import EMBEDDING_DIMENSION
from src.ingestion import insert_chunks


class FakeCursor:
    def __init__(self) -> None:
        self.calls = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        return None

    def executemany(self, statement, rows) -> None:
        self.calls.append((statement, rows))


class FakeConnection:
    def __init__(self) -> None:
        self.cursor_instance = FakeCursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        return None

    def cursor(self) -> FakeCursor:
        return self.cursor_instance


class InsertChunksTests(unittest.TestCase):
    @patch("src.ingestion.register_vector")
    @patch("src.ingestion.connect")
    def test_embeds_and_upserts_chunks_in_batches(
        self, connect: Mock, register_vector: Mock
    ) -> None:
        connection = FakeConnection()
        connect.return_value = connection
        embedder = Mock()
        embedder.encode_batch.side_effect = [
            np.zeros((2, EMBEDDING_DIMENSION), dtype=np.float32),
            np.ones((1, EMBEDDING_DIMENSION), dtype=np.float32),
        ]
        chunks = [
            {"filename": "lesson.md", "start": 0, "content": "first"},
            {"filename": "lesson.md", "start": 1000, "content": "second"},
            {"filename": "other.md", "start": 0, "content": "third"},
        ]

        count = insert_chunks(
            chunks,
            database_url="postgresql://test",
            embedder=embedder,
            batch_size=2,
        )

        self.assertEqual(count, 3)
        connect.assert_called_once_with("postgresql://test")
        register_vector.assert_called_once_with(connection)
        self.assertEqual(
            embedder.encode_batch.call_args_list,
            [
                call(["first", "second"]),
                call(["third"]),
            ],
        )
        self.assertEqual(len(connection.cursor_instance.calls), 2)
        first_rows = connection.cursor_instance.calls[0][1]
        self.assertEqual(first_rows[0][:3], ("lesson.md", 0, "first"))
        self.assertEqual(first_rows[1][:3], ("lesson.md", 1000, "second"))
        self.assertEqual(first_rows[0][3].shape, (EMBEDDING_DIMENSION,))

    @patch("src.ingestion.connect")
    def test_empty_input_does_not_open_database_connection(
        self, connect: Mock
    ) -> None:
        self.assertEqual(insert_chunks([], embedder=Mock()), 0)
        connect.assert_not_called()

    @patch("src.ingestion.connect")
    def test_rejects_missing_required_chunk_fields(self, connect: Mock) -> None:
        embedder = Mock()
        embedder.encode_batch.return_value = np.zeros(
            (1, EMBEDDING_DIMENSION), dtype=np.float32
        )

        with self.assertRaisesRegex(ValueError, "filename"):
            insert_chunks([{"start": 0, "content": "text"}], embedder=embedder)

        connect.assert_not_called()
        embedder.encode_batch.assert_not_called()

    @patch("src.ingestion.register_vector")
    @patch("src.ingestion.connect")
    def test_rejects_wrong_embedding_dimension(
        self, connect: Mock, register_vector: Mock
    ) -> None:
        connect.return_value = FakeConnection()
        embedder = Mock()
        embedder.encode_batch.return_value = np.zeros((1, 10), dtype=np.float32)

        with self.assertRaisesRegex(ValueError, "expected"):
            insert_chunks(
                [{"filename": "lesson.md", "start": 0, "content": "text"}],
                embedder=embedder,
            )


if __name__ == "__main__":
    unittest.main()
