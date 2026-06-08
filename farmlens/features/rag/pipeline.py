from __future__ import annotations

from farmlens.core.config import Settings
from farmlens.features.rag.exceptions import RAGException
from farmlens.features.rag.schemas import RAGResponse


class RAGPipeline:
    """Class-based RAG pipeline. Single instance per app."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._embedder = None
        self._db = None
        self._chain = None

    def initialize(self) -> None:
        """Load embedder and vector DB. Called once at startup."""
        raise NotImplementedError

    def answer(self, question: str, language: str = "hi") -> RAGResponse:
        """Answer a farming question using RAG."""
        raise NotImplementedError

    def ingest(self, pdf_dir: str) -> int:
        """Ingest PDFs from a directory. Returns number of chunks created."""
        raise NotImplementedError

    def evaluate(self, eval_dataset: list[dict]) -> dict[str, float]:
        """Run RAGAS evaluation. Returns a metrics dict."""
        raise NotImplementedError

    @property
    def is_ready(self) -> bool:
        """True if the vector DB is loaded and ready."""
        return self._db is not None
