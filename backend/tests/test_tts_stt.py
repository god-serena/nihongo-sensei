"""Tests for the WhisperTranscriber STT integration."""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock

from app.tts_stt import WhisperTranscriber


class TestWhisperTranscriber:
    """Test suite for WhisperTranscriber."""

    def test_init_defaults(self) -> None:
        """Verify default constructor parameters."""
        transcriber = WhisperTranscriber()
        assert transcriber._model is None
        assert transcriber._model_size == "base"
        assert transcriber._device == "cpu"
        assert transcriber._compute_type == "int8"

    @patch.object(WhisperTranscriber, "model", new_callable=PropertyMock)
    def test_transcribe_joins_segments(self, mock_model: PropertyMock) -> None:
        """transcribe() should concatenate all segment texts with spaces."""
        # Build fake segments
        seg1 = MagicMock()
        seg2 = MagicMock()
        seg1.text = "こんにちは"
        seg2.text = "世界"
        mock_model.return_value.transcribe.return_value = [seg1, seg2]

        transcriber = WhisperTranscriber()
        result = transcriber.transcribe("/tmp/test.wav")

        assert result == "こんにちは 世界"
        mock_model.assert_called_once()

    def test_transcribe_bytes_writes_temp_file_and_calls_transcribe(self) -> None:
        """transcribe_bytes() should write bytes to a temp file and call transcribe()."""
        audio_data = b"RIFF... (fake WAV header)"  # noqa: E501

        with patch.object(WhisperTranscriber, "transcribe") as mock_transcribe:
            mock_transcribe.return_value = "hello world"
            result = WhisperTranscriber().transcribe_bytes(audio_data)

        assert result == "hello world"
        # Verify transcribe was called once (with the temp file path)
        assert mock_transcribe.call_count == 1
        args, _ = mock_transcribe.call_args
        assert args[0].endswith(".wav")

    def test_transcribe_skips_empty_segments(self) -> None:
        """Empty-text segments should not contribute to output."""
        seg_with_text = MagicMock()
        seg_no_text = MagicMock()
        seg_with_text.text = "hello"
        seg_no_text.text = ""  # empty segment
        with patch.object(WhisperTranscriber, "model") as mock_model:
            mock_model.transcribe.return_value = [seg_with_text, seg_no_text]
            result = WhisperTranscriber().transcribe("/tmp/test.wav")

        assert result == "hello"

    def test_lazy_model_loading(self) -> None:
        """The model should only be instantiated on first use."""
        transcriber = WhisperTranscriber()
        assert transcriber._model is None

        with patch("app.tts_stt.WhisperModel") as mock_whisper:
            _ = transcriber.model  # triggers lazy load
            mock_whisper.assert_called_once()
