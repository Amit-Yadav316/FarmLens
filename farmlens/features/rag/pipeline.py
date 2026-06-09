from __future__ import annotations

from typing import Any

from farmlens.core.config import Settings
from farmlens.features.rag.exceptions import RAGException
from farmlens.features.rag.ingestion import PDFIngestion
from farmlens.features.rag.schemas import RAGResponse, SourceDocument

_EMBED_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


class RAGPipeline:
    """Class-based RAG pipeline. Single instance per app."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._embedder: Any = None
        self._db: Any = None
        self._chain: Any = None

    def initialize(self) -> None:
        """Load embedder, vector DB, and chain. Called once at startup."""
        try:
            self._embedder = self._load_embedder()
            self._db = self._load_db()
            self._chain = self._build_chain()
        except Exception as e:
            raise RAGException(f"RAG initialization failed: {e}") from e

    def answer(self, question: str, language: str = "hi") -> RAGResponse:
        """Answer a farming question using RAG."""
        if not self.is_ready:
            raise RAGException("Pipeline not initialized — call initialize() first")
        try:
            result = self._chain.invoke({"query": question})
            return self._build_response(result, language)
        except Exception as e:
            raise RAGException(f"RAG answer failed: {e}") from e

    def ingest(self, pdf_dir: str) -> int:
        """Ingest PDFs from a directory. Returns number of chunks created."""
        return PDFIngestion(self._settings).run(pdf_dir)

    def evaluate(self, eval_dataset: list[dict]) -> dict[str, float]:
        """Run RAGAS evaluation. Returns a metrics dict."""
        raise NotImplementedError

    @property
    def is_ready(self) -> bool:
        """True if the vector DB is loaded and ready."""
        return self._db is not None

    def _load_embedder(self) -> Any:
        """Load the multilingual HuggingFace embedding model."""
        from langchain_community.embeddings import HuggingFaceEmbeddings
        return HuggingFaceEmbeddings(model_name=_EMBED_MODEL)

    def _load_db(self) -> Any:
        """Connect to the persisted ChromaDB vector store."""
        from langchain_community.vectorstores import Chroma
        return Chroma(
            persist_directory=self._settings.chroma_db_path,
            embedding_function=self._embedder,
        )

    def _build_chain(self) -> Any:
        """Build a RetrievalQA chain backed by Ollama and ChromaDB."""
        from langchain.chains import RetrievalQA
        from langchain_ollama import OllamaLLM
        llm = OllamaLLM(
            base_url=self._settings.ollama_base_url,
            model=self._settings.ollama_model,
        )
        retriever = self._db.as_retriever(search_kwargs={"k": 3})
        return RetrievalQA.from_chain_type(
            llm=llm, retriever=retriever, return_source_documents=True,
        )

    def _build_response(self, result: dict, language: str) -> RAGResponse:
        """Map a RetrievalQA result dict to a RAGResponse."""
        sources = [
            SourceDocument(
                content=doc.page_content,
                source=doc.metadata.get("source", ""),
                page=doc.metadata.get("page"),
            )
            for doc in result.get("source_documents", [])
        ]
        return RAGResponse(answer=result.get("result", ""), sources=sources, language=language)
