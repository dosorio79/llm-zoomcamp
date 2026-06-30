import unittest

import numpy as np

from src.rerank import CrossEncoderReranker
from src.retrieval import SearchResult


class FakeInput:
    def __init__(self, name: str) -> None:
        self.name = name


class FakeEncoding:
    def __init__(self, index: int) -> None:
        self.ids = [101, index, 102]
        self.attention_mask = [1, 1, 1]
        self.type_ids = [0, 0, 1]


class FakeTokenizer:
    def __init__(self) -> None:
        self.pairs = []

    def encode_batch(self, pairs):
        self.pairs = pairs
        return [FakeEncoding(index) for index, _ in enumerate(pairs, start=1)]


class FakeSession:
    def __init__(self, logits) -> None:
        self.logits = logits
        self.feed = None

    def get_inputs(self):
        return [
            FakeInput("input_ids"),
            FakeInput("attention_mask"),
            FakeInput("token_type_ids"),
        ]

    def run(self, output_names, feed):
        self.feed = feed
        return [np.asarray(self.logits, dtype=np.float32)]


def make_result(document_id: int, content: str, score: float = 0.0) -> SearchResult:
    return {
        "id": document_id,
        "filename": f"doc-{document_id}.md",
        "start": document_id,
        "content": content,
        "score": score,
    }


class CrossEncoderRerankerTests(unittest.TestCase):
    def test_scores_query_document_pairs_in_batch(self) -> None:
        tokenizer = FakeTokenizer()
        session = FakeSession([[0.1], [0.9]])
        reranker = CrossEncoderReranker(tokenizer=tokenizer, session=session)

        scores = reranker.score("question", ["first", "second"])

        self.assertEqual(tokenizer.pairs, [("question", "first"), ("question", "second")])
        self.assertEqual(scores, [0.10000000149011612, 0.8999999761581421])
        np.testing.assert_array_equal(
            session.feed["input_ids"],
            np.asarray([[101, 1, 102], [101, 2, 102]], dtype=np.int64),
        )

    def test_rerank_sorts_descending_and_replaces_scores(self) -> None:
        reranker = CrossEncoderReranker(
            tokenizer=FakeTokenizer(),
            session=FakeSession([[0.2], [0.8], [0.4]]),
        )

        results = reranker.rerank(
            "question",
            [
                make_result(1, "first", score=99.0),
                make_result(2, "second", score=0.0),
                make_result(3, "third", score=0.0),
            ],
            top_k=2,
        )

        self.assertEqual([result["id"] for result in results], [2, 3])
        self.assertEqual(results[0]["score"], 0.800000011920929)

    def test_rerank_preserves_original_order_for_ties(self) -> None:
        reranker = CrossEncoderReranker(
            tokenizer=FakeTokenizer(),
            session=FakeSession([[0.5], [0.5], [0.5]]),
        )

        results = reranker.rerank(
            "question",
            [make_result(1, "first"), make_result(2, "second"), make_result(3, "third")],
            top_k=3,
        )

        self.assertEqual([result["id"] for result in results], [1, 2, 3])

    def test_rerank_returns_empty_list_for_empty_candidates(self) -> None:
        reranker = CrossEncoderReranker(
            tokenizer=FakeTokenizer(),
            session=FakeSession([]),
        )

        self.assertEqual(reranker.rerank("question", [], top_k=5), [])


if __name__ == "__main__":
    unittest.main()
