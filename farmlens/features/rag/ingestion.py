from __future__ import annotations

from farmlens.core.config import Settings
from farmlens.features.rag.exceptions import RAGException


class PDFIngestion:
    """Loads, splits, and embeds ICAR PDF documents into ChromaDB."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._chunk_size: int = 500
        self._chunk_overlap: int = 50

    def run(self, pdf_dir: str) -> int:
        """Ingest all PDFs in a directory. Returns total chunk count."""
        raise NotImplementedError

    def _load_pdf(self, path: str) -> list[str]:
        """Load and split a single PDF into text chunks."""
        raise NotImplementedError

    def _embed_and_store(self, chunks: list[str], source: str) -> int:
        """Embed chunks and persist them to ChromaDB."""
        raise NotImplementedError
