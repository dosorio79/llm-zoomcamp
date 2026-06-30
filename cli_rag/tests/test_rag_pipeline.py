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


class FakeReranker:
    def __init__(self) -> None:
        self.calls = []

    def rerank(
        self,
        query: str,
        results: list[SearchResult],
        top_k: int = 5,
    ) -> list[SearchResult]:
        self.calls.append((query, results, top_k))
        return [
            {
                "id": 2,
                "filename": "reranked.md",
                "start": 10,
                "content": "reranked",
                "score": 0.99,
            }
        ]


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

    def test_retrieve_without_rerank_uses_requested_top_k(self) -> None:
        pipeline = RAGPipeline(rerank=False)
        retriever = FakeRetriever()
        pipeline.retriever = retriever

        pipeline.retrieve("question", top_k=3)

        self.assertEqual(retriever.calls, [("question", 3)])

    def test_retrieve_with_rerank_expands_candidates_and_trims_results(self) -> None:
        reranker = FakeReranker()
        pipeline = RAGPipeline(
            rerank=True,
            reranker=reranker,
            rerank_candidate_multiplier=4,
        )
        retriever = FakeRetriever()
        pipeline.retriever = retriever

        results = pipeline.retrieve("question", top_k=3)

        self.assertEqual(retriever.calls, [("question", 12)])
        self.assertEqual(reranker.calls, [("question", retriever.results, 3)])
        self.assertEqual([result["id"] for result in results], [2])


if __name__ == "__main__":
    unittest.main()
