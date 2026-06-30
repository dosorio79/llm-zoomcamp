"""Download the local ONNX cross-encoder reranker model."""

from pathlib import Path

from ..config import RERANKER_MODEL_PATH, RERANKER_MODEL_REPO
from ..models import download_onnx_model


def main() -> None:
    model_path = Path(RERANKER_MODEL_PATH)
    download_onnx_model(RERANKER_MODEL_REPO, dest=model_path.parent.parent)


if __name__ == "__main__":
    main()
