from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from farmlens.features.asr.exceptions import ASRException
from farmlens.features.asr.service import ASRService

_PATCH = "faster_whisper.WhisperModel"


def _make_segment(text: str) -> MagicMock:
    seg = MagicMock()
    seg.text = text
    return seg


def _make_model_mock(segments: list[str], language: str = "hi") -> MagicMock:
    mock_model = MagicMock()
    info = MagicMock()
    info.language = language
    mock_model.transcribe.return_value = ([_make_segment(s) for s in segments], info)
    return mock_model


class TestASRService:
    """Tests for ASRService."""

    def test_transcribe_returns_transcript(self, settings) -> None:
        """transcribe returns a TranscriptResponse with text and language."""
        service = ASRService(settings)
        with patch(_PATCH) as mock_cls:
            mock_cls.return_value = _make_model_mock(["नमस्ते"], "hi")
            result = service.transcribe(b"fake_audio", language="hi")
        assert result.text == "नमस्ते"
        assert result.language == "hi"

    def test_transcribe_joins_multiple_segments(self, settings) -> None:
        """Multiple segments are joined with spaces into a single text."""
        service = ASRService(settings)
        with patch(_PATCH) as mock_cls:
            mock_cls.return_value = _make_model_mock(["गेहूं में", "कौन सी खाद डालें"], "hi")
            result = service.transcribe(b"fake_audio", language="hi")
        assert result.text == "गेहूं में कौन सी खाद डालें"

    def test_model_is_none_before_first_call(self, settings) -> None:
        """Model is not loaded until transcribe is called."""
        service = ASRService(settings)
        assert service._model is None

    def test_model_loaded_only_once_across_calls(self, settings) -> None:
        """Calling transcribe twice loads the WhisperModel only once."""
        service = ASRService(settings)
        with patch(_PATCH) as mock_cls:
            mock_cls.return_value = _make_model_mock(["test"])
            service.transcribe(b"audio1")
            service.transcribe(b"audio2")
        assert mock_cls.call_count == 1

    def test_empty_segments_returns_empty_text(self, settings) -> None:
        """Audio with no speech returns an empty text string."""
        service = ASRService(settings)
        with patch(_PATCH) as mock_cls:
            mock_cls.return_value = _make_model_mock([])
            result = service.transcribe(b"silence")
        assert result.text == ""

    def test_model_load_failure_raises_asr_exception(self, settings) -> None:
        """WhisperModel init failure raises ASRException."""
        service = ASRService(settings)
        with patch(_PATCH, side_effect=RuntimeError("no model")):
            with pytest.raises(ASRException, match="Failed to load"):
                service.transcribe(b"audio")

    def test_transcribe_error_raises_asr_exception(self, settings) -> None:
        """Transcription runtime error raises ASRException."""
        service = ASRService(settings)
        with patch(_PATCH) as mock_cls:
            mock_model = MagicMock()
            mock_model.transcribe.side_effect = RuntimeError("decode error")
            mock_cls.return_value = mock_model
            with pytest.raises(ASRException, match="Transcription failed"):
                service.transcribe(b"bad_audio")
