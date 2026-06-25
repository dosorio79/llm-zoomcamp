import unittest
from unittest.mock import patch

from src.retrieval import (
    BaseRetriever,
    HybridRetriever,
    TextRetriever,
    VectorRetriever,
)


class RetrieverScaffoldTests(unittest.TestCase):
    def test_retrievers_share_the_base_class(self) -> None:
        self.assertTrue(issubclass(TextRetriever, BaseRetriever))
        self.assertTrue(issubclass(VectorRetriever, BaseRetriever))
        self.assertTrue(issubclass(HybridRetriever, BaseRetriever))

    def test_blank_queries_return_no_results(self) -> None:
        for retriever in (TextRetriever(), VectorRetriever(), HybridRetriever()):
            with self.subTest(retriever=type(retriever).__name__):
                self.assertEqual(retriever.search("   "), [])

    def test_non_empty_queries_reach_explicit_placeholders(self) -> None:
        expected_messages = {
            TextRetriever: "BM25 retrieval SQL is not implemented yet.",
            VectorRetriever: (
                "Query embedding and vector retrieval SQL are not implemented yet."
            ),
            HybridRetriever: "Hybrid result fusion is not implemented yet.",
        }

        for retriever_type, message in expected_messages.items():
            with self.subTest(retriever=retriever_type.__name__):
                with self.assertRaisesRegex(NotImplementedError, message):
                    retriever_type().search("postgres")

    def test_construction_does_not_open_a_database_connection(self) -> None:
        with patch("psycopg.connect") as connect:
            TextRetriever()
            VectorRetriever()
            HybridRetriever()

        connect.assert_not_called()


if __name__ == "__main__":
    unittest.main()
