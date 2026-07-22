"""Speech-to-Text (STT) integration using faster-whisper."""

import io
import tempfile
from pathlib import Path

import edge_tts
from faster_whisper import WhisperModel


class WhisperTranscriber:
    """Local STT transcriber backed by CTranslate2/faster-whisper.

    Creates a model instance on first use and caches it for reuse.
    All transcription is performed on CPU (no GPU required).
    """

    def __init__(
        self,
        model_size: str = "base",
        device: str = "cpu",
        compute_type: str = "int8",
    ) -> None:
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


class TTSGenerator:
    """Text-to-Speech generator using edge-tts (Microsoft neural voices).

    Provides Japanese voice synthesis via the Edge-TTS library.
    Default voice is `ja-JP-NanamiNeural` — a natural-sounding female
    Japanese voice. Voice, rate, and volume are configurable at init time.
    """

    def __init__(
        self,
        voice: str = "ja-JP-NanamiNeural",
        rate: str = "+0%",
        volume: str = "+0%",
    ) -> None:
        self._voice = voice
        self._rate = rate
        self._volume = volume

    async def synthesize(self, text: str) -> bytes:
        """Synthesise speech for *text* and return raw MP3 bytes.

        Args:
            text: The text to convert to speech.

        Returns:
            Raw MP3 audio bytes.
        """
        communicate = edge_tts.Communicate(
            text,
            self._voice,
        )
        # Build a byte buffer from the streaming chunks.
        audio_io = io.BytesIO()
        async for chunk in communicate.stream():
            if isinstance(chunk, bytes):
                audio_io.write(chunk)
        return audio_io.getvalue()

    async def synthesize_to_file(self, text: str, output_path: str) -> None:
        """Synthesise speech and save it to a file.

        Args:
            text: The text to convert to speech.
            output_path: File path where the MP3 will be written.
        """
        audio_bytes = await self.synthesize(text)
        Path(output_path).write_bytes(audio_bytes)
