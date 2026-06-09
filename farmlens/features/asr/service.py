from __future__ import annotations

import io

from farmlens.core.config import Settings
from farmlens.features.asr.exceptions import ASRException
from farmlens.features.asr.schemas import TranscriptResponse


class ASRService:
    """Transcribes audio to text using faster-whisper."""

    def __init__(self, settings: Settings) -> None:
        self._model_size: str = "small"
        self._model = None  # loaded lazily on first transcribe call

    def transcribe(self, audio_bytes: bytes, language: str = "hi") -> TranscriptResponse:
        """Transcribe audio bytes to text in the given language."""
        self._load_model()
        try:
            audio_io = io.BytesIO(audio_bytes)
            segments, info = self._model.transcribe(audio_io, language=language)
            text = " ".join(seg.text.strip() for seg in segments)
            return TranscriptResponse(text=text, language=info.language)
        except Exception as e:
            raise ASRException(f"Transcription failed: {e}") from e

    def _load_model(self) -> None:
        """Load the Whisper model on first use (CPU, int8 quantised)."""
        if self._model is not None:
            return
        try:
            from faster_whisper import WhisperModel
            self._model = WhisperModel(self._model_size, device="cpu", compute_type="int8")
        except Exception as e:
            raise ASRException(f"Failed to load Whisper model: {e}") from e
