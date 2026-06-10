from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from farmlens.features.rag.exceptions import RAGException
from farmlens.features.rag.ingestion import PDFIngestion
from farmlens.features.rag.pipeline import RAGPipeline


def _make_source_doc(
    content: str = "test chunk", source: str = "icar.pdf", page: int = 1
) -> MagicMock:
    doc = MagicMock()
    doc.page_content = content
    doc.metadata = {"source": source, "page": page}
    return doc


# ─── RAGPipeline tests ────────────────────────────────────────────────────────


class TestRAGPipeline:
    """Tests for RAGPipeline."""

    def test_is_ready_false_before_initialize(self, settings) -> None:
        """Pipeline is not ready until initialize() is called."""
        pipeline = RAGPipeline(settings)
        assert pipeline.is_ready is False

    def test_is_ready_true_after_initialize(self, settings) -> None:
        """Pipeline is ready after initialize() completes."""
        pipeline = RAGPipeline(settings)
        pipeline._load_embedder = MagicMock(return_value=MagicMock())
        pipeline._load_db = MagicMock(return_value=MagicMock())
        pipeline._build_chain = MagicMock(return_value=MagicMock())
        pipeline.initialize()
        assert pipeline.is_ready is True

    def test_initialize_failure_raises_rag_exception(self, settings) -> None:
        """Initialization error is wrapped in RAGException."""
        pipeline = RAGPipeline(settings)
        pipeline._load_embedder = MagicMock(side_effect=RuntimeError("no embedder"))
        with pytest.raises(RAGException, match="initialization failed"):
            pipeline.initialize()

    def test_answer_raises_if_not_initialized(self, settings) -> None:
        """answer() raises RAGException when called before initialize()."""
        pipeline = RAGPipeline(settings)
        with pytest.raises(RAGException, match="not initialized"):
            pipeline.answer("गेहूं में क्या डालें")

    def test_answer_returns_rag_response(self, settings) -> None:
        """answer() returns a RAGResponse with answer text and sources."""
        pipeline = RAGPipeline(settings)
        pipeline._load_embedder = MagicMock(return_value=MagicMock())
        pipeline._load_db = MagicMock(return_value=MagicMock())
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = {
            "result": "गेहूं में DAP खाद डालें",
            "source_documents": [_make_source_doc()],
        }
        pipeline._build_chain = MagicMock(return_value=mock_chain)
        pipeline.initialize()
        result = pipeline.answer("गेहूं में क्या डालें", language="hi")
        assert result.answer == "गेहूं में DAP खाद डालें"
        assert result.language == "hi"
        assert len(result.sources) == 1
        assert result.sources[0].source == "icar.pdf"

    def test_answer_maps_source_document_fields(self, settings) -> None:
        """Source documents are correctly mapped to SourceDocument schema."""
        pipeline = RAGPipeline(settings)
        pipeline._load_embedder = MagicMock(return_value=MagicMock())
        pipeline._load_db = MagicMock(return_value=MagicMock())
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = {
            "result": "answer",
            "source_documents": [_make_source_doc("chunk text", "doc.pdf", 5)],
        }
        pipeline._build_chain = MagicMock(return_value=mock_chain)
        pipeline.initialize()
        result = pipeline.answer("question")
        assert result.sources[0].content == "chunk text"
        assert result.sources[0].page == 5

    def test_ingest_delegates_to_pdf_ingestion(self, settings) -> None:
        """ingest() delegates to PDFIngestion.run() and returns chunk count."""
        pipeline = RAGPipeline(settings)
        with patch.object(PDFIngestion, "run", return_value=42) as mock_run:
            count = pipeline.ingest("./data/pdfs")
        mock_run.assert_called_once_with("./data/pdfs")
        assert count == 42

    def test_answer_chain_error_raises_rag_exception(self, settings) -> None:
        """Chain invocation error is wrapped in RAGException."""
        pipeline = RAGPipeline(settings)
        pipeline._load_embedder = MagicMock(return_value=MagicMock())
        pipeline._load_db = MagicMock(return_value=MagicMock())
        mock_chain = MagicMock()
        mock_chain.invoke.side_effect = RuntimeError("ollama down")
        pipeline._build_chain = MagicMock(return_value=mock_chain)
        pipeline.initialize()
        with pytest.raises(RAGException, match="answer failed"):
            pipeline.answer("question")


# ─── PDFIngestion tests ───────────────────────────────────────────────────────


class TestPDFIngestion:
    """Tests for PDFIngestion."""

    def test_run_raises_if_directory_not_found(self, settings) -> None:
        """run() raises RAGException when the directory does not exist."""
        ingestion = PDFIngestion(settings)
        with pytest.raises(RAGException, match="not found"):
            ingestion.run("/nonexistent/path")

    def test_run_raises_if_no_pdfs(self, settings, tmp_path) -> None:
        """run() raises RAGException when the directory has no PDF files."""
        ingestion = PDFIngestion(settings)
        with pytest.raises(RAGException, match="No PDFs found"):
            ingestion.run(str(tmp_path))

    def test_run_returns_total_chunk_count(self, settings, tmp_path) -> None:
        """run() returns the total number of chunks across all PDFs."""
        (tmp_path / "icar1.pdf").write_bytes(b"fake")
        (tmp_path / "icar2.pdf").write_bytes(b"fake")
        ingestion = PDFIngestion(settings)
        ingestion._get_embedder = MagicMock(return_value=MagicMock())
        ingestion._load_pdf = MagicMock(return_value=["c1", "c2", "c3"])
        ingestion._embed_and_store = MagicMock(return_value=3)
        result = ingestion.run(str(tmp_path))
        assert result == 6
        assert ingestion._embed_and_store.call_count == 2

    def test_embedder_is_requested_once_for_multiple_pdfs(self, settings, tmp_path) -> None:
        """_get_embedder is called only once even when ingesting multiple PDFs."""
        (tmp_path / "a.pdf").write_bytes(b"fake")
        (tmp_path / "b.pdf").write_bytes(b"fake")
        ingestion = PDFIngestion(settings)
        ingestion._get_embedder = MagicMock(return_value=MagicMock())
        ingestion._load_pdf = MagicMock(return_value=["chunk"])
        ingestion._embed_and_store = MagicMock(return_value=1)
        ingestion.run(str(tmp_path))
        ingestion._get_embedder.assert_called_once()
