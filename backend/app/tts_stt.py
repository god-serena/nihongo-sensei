"""Speech-to-Text (STT) integration using faster-whisper."""

import tempfile
from pathlib import Path

from faster_whisper import WhisperModel


class WhisperTranscriber:
    """Local STT transcriber backed by CTranslate2/faster-whisper.

    Creates a model instance on first use and caches it for reuse.
    All transcription is performed on CPU (no GPU required).
    """

    def __init__(self, model_size: str = "base", device: str = "cpu", compute_type: str = "int8") -> None:
        self._model_size = model_size
        self._device = device
        self._compute_type = compute_type
        # Lazily initialise the model so that instantiation is cheap.
        self._model: WhisperModel | None = None

    @property
    def model(self) -> WhisperModel:
        if self._model is None:
            self._model = WhisperModel(
                self._model_size,
                device=self._device,
                compute_type=self._compute_type,
                download_root=Path(tempfile.gettempdir()) / "faster_whisper",
            )
        return self._model

    def transcribe(self, audio_path: str) -> str:
        """Transcribe an audio file and return the full transcript text.

        Args:
            audio_path: Path to a WAV/MP3/M4A file.

        Returns:
            The concatenated text from all recognised segments.
        """
        segments = self.model.transcribe(audio_path)
        return " ".join(segment.text for segment in segments if segment.text)

    def transcribe_bytes(self, audio_bytes: bytes, suffix: str = ".wav") -> str:
        """Transcribe raw audio bytes by writing them to a temporary file.

        Args:
            audio_bytes: Raw audio data (e.g. WAV or MP3).
            suffix: File extension for the temp file.

        Returns:
            The concatenated text from all recognised segments.
        """
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name
        try:
            return self.transcribe(tmp_path)
        finally:
            Path(tmp_path).unlink(missing_ok=True)
