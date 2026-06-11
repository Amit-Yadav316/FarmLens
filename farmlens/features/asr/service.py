from __future__ import annotations

import io
from typing import TYPE_CHECKING

from farmlens.features.asr.exceptions import ASRException
from farmlens.features.asr.schemas import TranscriptResponse

if TYPE_CHECKING:
    from faster_whisper import WhisperModel  # type: ignore[import-untyped]


class ASRService:
    """Transcribes audio to text using faster-whisper."""

    def __init__(self) -> None:
        self._model_size: str = "small"
        self._model: WhisperModel | None = None  # loaded lazily on first transcribe call

    def transcribe(self, audio_bytes: bytes, language: str = "hi") -> TranscriptResponse:
        """Transcribe audio bytes to text in the given language."""
        self._load_model()
        if self._model is None:  # _load_model raises on failure; this narrows the type
            raise ASRException("Whisper model is not loaded")
        try:
            audio_io = io.BytesIO(audio_bytes)
            segments, info = self._model.transcribe(audio_io, language=language)
            text = " ".join(seg.text.strip() for seg in segments)
            return TranscriptResponse(text=text, language=info.language)
        except (RuntimeError, ValueError, OSError) as e:
            raise ASRException(f"Transcription failed: {e}") from e

    def _load_model(self) -> None:
        """Load the Whisper model on first use (CPU, int8 quantised)."""
        if self._model is not None:
            return
        try:
            from faster_whisper import WhisperModel  # type: ignore[import-untyped]

            self._model = WhisperModel(self._model_size, device="cpu", compute_type="int8")
        except (ImportError, RuntimeError, OSError) as e:
            raise ASRException(f"Failed to load Whisper model: {e}") from e
