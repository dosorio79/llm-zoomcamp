from pathlib import Path

from ..models import download_onnx_model

DEFAULT_MODEL_DIR = Path(__file__).resolve().parent / "models"


if __name__ == "__main__":
    download_onnx_model("Xenova/all-MiniLM-L6-v2", dest=DEFAULT_MODEL_DIR)
