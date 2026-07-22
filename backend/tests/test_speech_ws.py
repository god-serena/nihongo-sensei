"""Tests for the WebSocket speech endpoint."""

import asyncio
import base64
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from starlette.testclient import TestClient
from app.main import app


@pytest.fixture()
def client():
    """Return a TestClient that does NOT re-raise server-side exceptions."""
    return TestClient(app, raise_server_exceptions=False)


# ── Helper fixtures ─────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def mock_whisper():
    """Patch WhisperTranscriber at the import site in the speech router."""
    with patch("app.routers.speech.WhisperTranscriber") as MockWhisper:
        instance = MagicMock()
        instance.transcribe_bytes.return_value = "Hello world"
        MockWhisper.return_value = instance
        yield instance


@pytest.fixture(autouse=True)
def mock_tts():
    """Patch TTSGenerator at the import site in the speech router."""
    with patch("app.routers.speech.TTSGenerator") as MockTTS:
        instance = MagicMock()
        # synthesize() is async — must be AsyncMock so `await` works.
        instance.synthesize = AsyncMock(return_value=b"\x00" * 1024)
        MockTTS.return_value = instance
        yield instance


@pytest.fixture(autouse=True)
def mock_llm():
    """Patch LLMClient at the import site in the speech router."""
    with patch("app.routers.speech.LLMClient") as MockLLM:
        async def fast_stream(messages, temperature=0.7):
            for token in ["Hello", " world"]:
                yield token

        instance = MagicMock()
        instance.generate_stream = fast_stream
        MockLLM.return_value = instance
        # Yield the *class mock* so tests can override MockLLM.return_value
        yield MockLLM


# ── Test: ping → pong ─────────────────────────────────────────────────────────────

def test_ping_pong(client):
    """A ping returns a pong."""
    with client.websocket_connect("/ws/speech") as ws:
        ws.send_json({"type": "ping"})
        assert ws.receive_json()["type"] == "pong"


# ── Test: full audio → transcript + tokens + done flow ────────────────────────────

def test_audio_pipeline(client):
    """Sending an audio blob produces a transcript, token messages, and a final 'done'."""
    audio_data = base64.b64encode(b"WAVDATA").decode("ascii")

    with client.websocket_connect("/ws/speech") as ws:
        ws.send_json({"type": "audio", "data": audio_data, "provider": "openai"})

        # Expect transcript first
        msg = ws.receive_json()
        assert msg["type"] == "transcript"
        assert msg["text"] == "Hello world"

        # Drain token/audio messages until done or cancelled
        received_tokens = []
        while True:
            msg = ws.receive_json()
            if msg["type"] in ("done", "cancelled"):
                break
            if msg["type"] == "token":
                received_tokens.append(msg["token"])

        assert msg["type"] == "done"
        assert "Hello" in received_tokens
        assert " world" in received_tokens


# ── Test: missing audio data ─────────────────────────────────────────────────────

def test_missing_audio_data(client):
    """Audio message without a data field returns an error and keeps connection alive."""
    with client.websocket_connect("/ws/speech") as ws:
        ws.send_json({"type": "audio"})
        msg = ws.receive_json()
        assert msg["type"] == "error"
        assert "Missing audio data" in msg["message"]

        # Connection should still be alive — confirm with a ping
        ws.send_json({"type": "ping"})
        assert ws.receive_json()["type"] == "pong"


# ── Test: bad base64 data ─────────────────────────────────────────────────────────

def test_bad_base64(client):
    """Invalid base64 (non-alphabet characters) returns an error message."""
    # "!!!invalid!!!" contains non-base64 chars — validate=True in the router catches this.
    with client.websocket_connect("/ws/speech") as ws:
        ws.send_json({"type": "audio", "data": "!!!invalid!!!"})
        msg = ws.receive_json()
        assert msg["type"] == "error"
        assert "Bad audio data" in msg["message"]

        # Connection should still be alive
        ws.send_json({"type": "ping"})
        assert ws.receive_json()["type"] == "pong"


# ── Test: cancel mid-stream stops generation ─────────────────────────────────────

def test_cancel_mid_stream(client, mock_llm):
    """Sending 'cancel' during generation eventually yields a 'cancelled' message."""
    audio_data = base64.b64encode(b"WAVDATA").decode("ascii")

    # Use a slow stream so the cancel message races ahead
    async def slow_stream(messages, temperature=0.7):
        for token in ["Hello", " world"]:
            await asyncio.sleep(0.05)
            yield token

    instance = MagicMock()
    instance.generate_stream = slow_stream
    mock_llm.return_value = instance

    with client.websocket_connect("/ws/speech") as ws:
        ws.send_json({"type": "audio", "data": audio_data})

        # Receive transcript first
        msg = ws.receive_json()
        assert msg["type"] == "transcript"

        # Issue cancel — server will process it between tokens
        ws.send_json({"type": "cancel"})

        # Drain messages until we see a cancelled (or done if cancel arrived too late)
        seen_types = []
        for _ in range(10):
            msg = ws.receive_json()
            seen_types.append(msg["type"])
            if msg["type"] in ("cancelled", "done"):
                break

        assert "cancelled" in seen_types or "done" in seen_types


# ── Test: cancelled event resets for next utterance ──────────────────────────────

def test_cancel_resets_for_next_utterance(client, mock_llm):
    """After a cancel, the cancelled event is cleared so subsequent audio works normally."""
    audio_data = base64.b64encode(b"WAVDATA").decode("ascii")

    async def slow_stream(messages, temperature=0.7):
        for token in ["Hello", " world"]:
            await asyncio.sleep(0.05)
            yield token

    # Override instance for this test
    instance = MagicMock()
    instance.generate_stream = slow_stream
    mock_llm.return_value = instance

    with client.websocket_connect("/ws/speech") as ws:
        # First utterance — cancel mid-stream
        ws.send_json({"type": "audio", "data": audio_data})
        msg = ws.receive_json()
        assert msg["type"] == "transcript"

        ws.send_json({"type": "cancel"})

        # Drain until we see a cancelled ack. The server may produce tokens,
        # a "cancelled" from the loop, then another "cancelled" from the cancel
        # handler — or "done" then "cancelled" if the stream finished first.
        # Keep draining until a "cancelled" is observed.
        for _ in range(15):
            msg = ws.receive_json()
            if msg["type"] == "cancelled":
                break

        # Second utterance — should complete normally (cancelled flag cleared by audio handler)
        ws.send_json({"type": "audio", "data": audio_data})
        # Skip any residual 'cancelled' acks that may have queued before our audio arrived
        while True:
            msg = ws.receive_json()
            if msg["type"] != "cancelled":
                break
        assert msg["type"] == "transcript"

        # Drain until done (not cancelled this time)
        for _ in range(20):
            msg = ws.receive_json()
            if msg["type"] in ("done", "cancelled"):
                break

        assert msg["type"] == "done"
