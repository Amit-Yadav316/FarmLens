from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from farmlens.core.config import Settings
from farmlens.features.rag.exceptions import RAGException

if TYPE_CHECKING:
    from langchain_core.documents import Document
    from langchain_core.embeddings import Embeddings

_EMBED_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


class PDFIngestion:
    """Loads, splits, and embeds ICAR PDF documents into ChromaDB."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._chunk_size: int = 500
        self._chunk_overlap: int = 50

    def run(self, pdf_dir: str) -> int:
        """Ingest all PDFs in a directory. Returns total chunk count."""
        pdf_path = Path(pdf_dir)
        if not pdf_path.exists():
            raise RAGException(f"PDF directory not found: {pdf_dir}")
        pdfs = list(pdf_path.glob("*.pdf"))
        if not pdfs:
            raise RAGException(f"No PDFs found in {pdf_dir}")
        embedder = self._get_embedder()
        total = 0
        for pdf in pdfs:
            chunks = self._load_pdf(str(pdf))
            total += self._embed_and_store(chunks, embedder)
        return total

    def _load_pdf(self, path: str) -> list[Document]:
        """Load and split a single PDF into Document chunks."""
        from langchain_community.document_loaders import PyPDFLoader
        from langchain_text_splitters import RecursiveCharacterTextSplitter

        loader = PyPDFLoader(path)
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self._chunk_size,
            chunk_overlap=self._chunk_overlap,
        )
        return splitter.split_documents(loader.load())

    def _embed_and_store(self, chunks: list[Document], embedder: Embeddings) -> int:
        """Embed chunks and persist them to ChromaDB. Returns chunk count."""
        from langchain_chroma import Chroma

        db = Chroma(
            persist_directory=self._settings.chroma_db_path,
            embedding_function=embedder,
        )
        db.add_documents(chunks)
        return len(chunks)

    def _get_embedder(self) -> Any:
        """Load the multilingual sentence embedding model."""
        from langchain_huggingface import HuggingFaceEmbeddings

        return HuggingFaceEmbeddings(model_name=_EMBED_MODEL)
