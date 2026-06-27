import unittest

from src.rag_pipeline import RAGPipeline
from src.retrieval import SearchResult


class FakeRetriever:
    def __init__(self) -> None:
        self.calls = []
        self.results: list[SearchResult] = [
            {
                "id": 1,
                "filename": "lesson.md",
                "start": 0,
                "content": "content",
                "score": 1.0,
            }
        ]

    def search(self, query: str, top_k: int = 5) -> list[SearchResult]:
        self.calls.append((query, top_k))
        return self.results


class RAGPipelineTests(unittest.TestCase):
    def test_build_context_includes_citable_source_labels(self) -> None:
        pipeline = RAGPipeline()

        context = pipeline.build_context(
            [
                {
                    "id": 1,
                    "filename": "lesson.md",
                    "start": 42,
                    "content": "Course content",
                    "score": 1.0,
                }
            ]
        )

        self.assertEqual(context, "Source: lesson.md:42\nContent: Course content")

    def test_retrieve_delegates_to_retriever_search(self) -> None:
        pipeline = RAGPipeline()
        retriever = FakeRetriever()
        pipeline.retriever = retriever

        results = pipeline.retrieve("   ", top_k=0)

        self.assertEqual(results, retriever.results)
        self.assertEqual(retriever.calls, [("   ", 0)])


if __name__ == "__main__":
    unittest.main()
