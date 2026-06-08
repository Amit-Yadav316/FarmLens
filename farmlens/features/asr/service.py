from __future__ import annotations

from farmlens.core.config import Settings
from farmlens.features.asr.exceptions import ASRException
from farmlens.features.asr.schemas import TranscriptResponse


class ASRService:
    """Transcribes audio to text using faster-whisper."""

    def __init__(self, settings: Settings) -> None:
        self._model_size: str = "small"
        self._model = None  # loaded lazily

    def transcribe(self, audio_bytes: bytes, language: str = "hi") -> TranscriptResponse:
        """Transcribe audio bytes to text."""
        raise NotImplementedError

    def _load_model(self) -> None:
        """Load the Whisper model on first use."""
        raise NotImplementedError
