import unittest
from unittest.mock import Mock, patch

import numpy as np

from src.config import BM25_INDEX_NAME, DATABASE_SCHEMA
from src.retrieval import (
    BaseRetriever,
    HybridRetriever,
    SearchResult,
    TextRetriever,
    VectorRetriever,
)


class FakeEmbedder:
    def encode(self, text: str, normalize: bool = True) -> list[float]:
        return [0.1, 0.2, 0.3]


class FakeRetriever:
    def __init__(self, results: list[SearchResult]) -> None:
        self.results = results
        self.calls = []

    def search(self, query: str, top_k: int = 5) -> list[SearchResult]:
        self.calls.append((query, top_k))
        return self.results


class FakeCursor:
    def __init__(self) -> None:
        self.calls = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        return None

    def execute(self, statement, params) -> None:
        self.calls.append((statement, params))

    def fetchall(self):
        return [(8, "lessons/vector.md", 240, "Vector content", 0.88)]


class FakeConnection:
    def __init__(self) -> None:
        self.cursor_instance = FakeCursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        return None

    def cursor(self) -> FakeCursor:
        return self.cursor_instance


class RetrieverScaffoldTests(unittest.TestCase):
    def test_retrievers_share_the_base_class(self) -> None:
        self.assertTrue(issubclass(TextRetriever, BaseRetriever))
        self.assertTrue(issubclass(VectorRetriever, BaseRetriever))
        self.assertTrue(issubclass(HybridRetriever, BaseRetriever))

    def test_blank_queries_return_no_results(self) -> None:
        for retriever in (TextRetriever(), VectorRetriever(), HybridRetriever()):
            with self.subTest(retriever=type(retriever).__name__):
                self.assertEqual(retriever.search("   "), [])

    @patch("src.retrieval.retrievers.fetch_all")
    def test_text_retriever_fetches_and_maps_search_results(self, fetch_all) -> None:
        fetch_all.return_value = [
            (7, "lessons/intro.md", 120, "PostgreSQL content", 0.42),
        ]

        results = TextRetriever(database_url="postgresql://test").search(
            "postgres",
            top_k=3,
        )

        fetch_all.assert_called_once()
        self.assertEqual(fetch_all.call_args.kwargs["database_url"], "postgresql://test")
        self.assertEqual(
            fetch_all.call_args.args[1],
            (
                "postgres",
                f"{DATABASE_SCHEMA}.{BM25_INDEX_NAME}",
                "postgres",
                f"{DATABASE_SCHEMA}.{BM25_INDEX_NAME}",
                3,
            ),
        )
        self.assertEqual(
            results,
            [
                {
                    "id": 7,
                    "filename": "lessons/intro.md",
                    "start": 120,
                    "content": "PostgreSQL content",
                    "score": 0.42,
                }
            ],
        )

    @patch("src.retrieval.retrievers.register_vector")
    @patch("src.retrieval.retrievers.connect")
    def test_vector_retriever_embeds_query_and_maps_results(
        self, connect: Mock, register_vector: Mock
    ) -> None:
        connection = FakeConnection()
        connect.return_value = connection

        results = VectorRetriever(
            database_url="postgresql://test",
            embedder=FakeEmbedder(),
        ).search("postgres", top_k=2)

        connect.assert_called_once_with("postgresql://test")
        register_vector.assert_called_once_with(connection)
        self.assertEqual(len(connection.cursor_instance.calls), 1)
        params = connection.cursor_instance.calls[0][1]
        np.testing.assert_array_equal(
            params[0],
            np.asarray([0.1, 0.2, 0.3], dtype=np.float32),
        )
        np.testing.assert_array_equal(params[1], params[0])
        self.assertEqual(params[2], 2)
        self.assertEqual(
            results,
            [
                {
                    "id": 8,
                    "filename": "lessons/vector.md",
                    "start": 240,
                    "content": "Vector content",
                    "score": 0.88,
                }
            ],
        )

    def test_hybrid_retriever_fuses_text_and_vector_results(self) -> None:
        text_results: list[SearchResult] = [
            {
                "id": 1,
                "filename": "a.md",
                "start": 0,
                "content": "text first",
                "score": 0.5,
            },
            {
                "id": 2,
                "filename": "b.md",
                "start": 0,
                "content": "shared",
                "score": 0.4,
            },
        ]
        vector_results: list[SearchResult] = [
            {
                "id": 2,
                "filename": "b.md",
                "start": 0,
                "content": "shared",
                "score": 0.9,
            },
            {
                "id": 3,
                "filename": "c.md",
                "start": 0,
                "content": "vector second",
                "score": 0.8,
            },
        ]
        text_retriever = FakeRetriever(text_results)
        vector_retriever = FakeRetriever(vector_results)

        results = HybridRetriever(
            text_retriever=text_retriever,
            vector_retriever=vector_retriever,
        ).search("postgres", top_k=2)

        self.assertEqual(text_retriever.calls, [("postgres", 2)])
        self.assertEqual(vector_retriever.calls, [("postgres", 2)])
        self.assertEqual([result["id"] for result in results], [2, 1])
        self.assertEqual(results[0]["score"], 1.5)

    def test_construction_does_not_open_a_database_connection(self) -> None:
        with patch("psycopg.connect") as connect:
            TextRetriever()
            VectorRetriever()
            HybridRetriever()

        connect.assert_not_called()


if __name__ == "__main__":
    unittest.main()
