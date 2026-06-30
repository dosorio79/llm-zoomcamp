"""Cross-encoder reranking for retrieved RAG candidates."""

from pathlib import Path
from typing import Any

import numpy as np
import onnxruntime as ort
from tokenizers import Tokenizer

from ..config import RERANKER_MODEL_PATH
from ..retrieval import SearchResult


class RerankerModelMissingError(FileNotFoundError):
    """Raised when the local reranker model has not been downloaded."""


class CrossEncoderReranker:
    """Score query-document pairs with a local ONNX cross encoder."""

    def __init__(
        self,
        path: str | Path = RERANKER_MODEL_PATH,
        session: Any | None = None,
        tokenizer: Any | None = None,
        max_length: int = 512,
    ) -> None:
        path = Path(path)
        self.path = path
        self.max_length = max_length
        self.tokenizer = tokenizer or self._load_tokenizer(path)
        self.session = session or self._load_session(path)
        self.input_names = {inp.name for inp in self.session.get_inputs()}

    def rerank(
        self,
        query: str,
        results: list[SearchResult],
        top_k: int = 5,
    ) -> list[SearchResult]:
        if not results or top_k <= 0:
            return []

        scores = self.score(query, [result["content"] for result in results])
        ranked = []

        for index, (result, score) in enumerate(zip(results, scores, strict=True)):
            ranked.append((index, {**result, "score": float(score)}))

        ranked.sort(key=lambda item: (-item[1]["score"], item[0]))
        return [result for _, result in ranked[:top_k]]

    def score(self, query: str, documents: list[str]) -> list[float]:
        if not documents:
            return []

        encoded = self._encode_pairs(query, documents)
        feed = self._build_feed(encoded)
        outputs = self.session.run(None, feed)
        logits = np.asarray(outputs[0], dtype=np.float32)
        return self._extract_scores(logits).astype(float).tolist()

    def _load_tokenizer(self, path: Path):
        tokenizer_path = path / "tokenizer.json"
        if not tokenizer_path.exists():
            raise RerankerModelMissingError(
                f"Reranker tokenizer not found at {tokenizer_path}. "
                "Run `make reranker-download` first."
            )

        tokenizer = Tokenizer.from_file(str(tokenizer_path))
        tokenizer.enable_padding()
        tokenizer.enable_truncation(max_length=self.max_length)
        return tokenizer

    def _load_session(self, path: Path):
        model_path = path / "model.onnx"
        if not model_path.exists():
            raise RerankerModelMissingError(
                f"Reranker ONNX model not found at {model_path}. "
                "Run `make reranker-download` first."
            )

        return ort.InferenceSession(
            str(model_path),
            providers=["CPUExecutionProvider"],
        )

    def _encode_pairs(self, query: str, documents: list[str]):
        pairs = [(query, document) for document in documents]
        return self.tokenizer.encode_batch(pairs)

    def _build_feed(self, encoded) -> dict[str, np.ndarray]:
        feed: dict[str, np.ndarray] = {}

        if "input_ids" in self.input_names:
            feed["input_ids"] = np.asarray([item.ids for item in encoded], dtype=np.int64)

        if "attention_mask" in self.input_names:
            feed["attention_mask"] = np.asarray(
                [item.attention_mask for item in encoded],
                dtype=np.int64,
            )

        if "token_type_ids" in self.input_names:
            feed["token_type_ids"] = np.asarray(
                [item.type_ids for item in encoded],
                dtype=np.int64,
            )

        return feed

    def _extract_scores(self, logits: np.ndarray) -> np.ndarray:
        if logits.ndim == 0:
            return logits.reshape(1)

        if logits.ndim == 1:
            return logits

        if logits.shape[1] == 1:
            return logits[:, 0]

        return logits[:, -1]
