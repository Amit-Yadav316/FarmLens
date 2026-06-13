from __future__ import annotations

from typing import Any

from farmlens.core.config import Settings
from farmlens.features.rag.exceptions import RAGException
from farmlens.features.rag.ingestion import PDFIngestion
from farmlens.features.rag.schemas import RAGResponse, SourceDocument

_EMBED_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# Hindi RAG prompt. The fine-tuned Ollama model wraps this in its own
# "### सवाल: / ### उत्तर:" template, so this supplies only the instruction +
# retrieved context + question, in Hindi, to match what the model was trained on.
_RAG_PROMPT = (
    "आप एक अनुभवी कृषि सलाहकार हैं। नीचे दी गई जानकारी के आधार पर किसान के "
    "प्रश्न का उत्तर सरल और स्पष्ट हिंदी में दें। केवल दी गई जानकारी का उपयोग करें; "
    "यदि उत्तर जानकारी में मौजूद नहीं है, तो विनम्रता से कहें कि आपके पास इसकी "
    "जानकारी नहीं है।\n\n"
    "संदर्भ:\n{context}\n\n"
    "प्रश्न: {question}"
)


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
        except (ImportError, OSError, ValueError, RuntimeError) as e:
            raise RAGException(f"RAG initialization failed: {e}") from e

    def answer(self, question: str, language: str = "hi") -> RAGResponse:
        """Answer a farming question using RAG."""
        if not self.is_ready:
            raise RAGException("Pipeline not initialized — call initialize() first")
        try:
            result = self._chain.invoke({"query": question})
            return self._build_response(result, language)
        except (RuntimeError, ValueError, ConnectionError, OSError) as e:
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
        from langchain_huggingface import HuggingFaceEmbeddings

        return HuggingFaceEmbeddings(model_name=_EMBED_MODEL)

    def _load_db(self) -> Any:
        """Connect to the persisted ChromaDB vector store."""
        from langchain_chroma import Chroma

        return Chroma(
            persist_directory=self._settings.chroma_db_path,
            embedding_function=self._embedder,
        )

    def _build_chain(self) -> Any:
        """Build a RetrievalQA chain backed by the configured LLM and ChromaDB."""
        try:  # langchain >= 1.0 moved legacy chains into langchain_classic
            from langchain_classic.chains import RetrievalQA
        except ImportError:  # langchain < 1.0
            from langchain.chains import RetrievalQA  # type: ignore[no-redef,import-not-found]
        from langchain_core.prompts import PromptTemplate

        retriever = self._db.as_retriever(search_kwargs={"k": 3})
        prompt = PromptTemplate(template=_RAG_PROMPT, input_variables=["context", "question"])
        return RetrievalQA.from_chain_type(
            llm=self._build_llm(),
            retriever=retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": prompt},
        )

    def _build_llm(self) -> Any:
        """Build the LLM backend: Ollama for local dev, llama.cpp for Spaces."""
        if self._settings.llm_backend == "llamacpp":
            from langchain_community.llms import LlamaCpp

            return LlamaCpp(
                model_path=self._resolve_gguf_path(),
                n_ctx=2048,
                max_tokens=self._settings.llm_max_tokens,
                temperature=0.7,
                verbose=False,
            )
        from langchain_ollama import OllamaLLM

        return OllamaLLM(
            base_url=self._settings.ollama_base_url,
            model=self._settings.ollama_model,
        )

    def _resolve_gguf_path(self) -> str:
        """Return a local GGUF path, pulling from HF Hub when no path is set."""
        if self._settings.gguf_path:
            return self._settings.gguf_path
        from huggingface_hub import hf_hub_download

        return hf_hub_download(
            repo_id=self._settings.gguf_repo_id,
            filename=self._settings.gguf_filename,
            token=self._settings.hf_token or None,
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
