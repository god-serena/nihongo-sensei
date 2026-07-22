"""WebSocket speech endpoint — real-time audio streaming with cancel support."""

import asyncio
import base64
import logging

from fastapi import APIRouter, WebSocket

from app.llm import LLMClient
from app.tts_stt import TTSGenerator, WhisperTranscriber

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws/speech")
async def websocket_speech(ws: WebSocket):
    """Real-time speech pipeline over WebSocket.

    Protocol::

        Client → Server                          Server → Client
        ──────────────────────────────────────────────────────────────
        {type:"audio", data:<base64>}   ───▶     transcript:{text}
                                                    token:{token}
                                                    audio:{data}
                                                    done
        {type:"cancel"}               ───▶       cancelled
        {type:"ping"}                 ───▶       pong

    V1 is push-to-talk: the client sends a single audio blob per utterance.
    """
    await ws.accept()

    # Shared, lazily instantiated engines (one Whisper model + one TTS instance).
    whisper = WhisperTranscriber()
    tts = TTSGenerator()

    # Per-connection cancellation flag; set externally via a "cancel" message.
    cancelled = asyncio.Event()

    try:
        while True:
            payload = await ws.receive_json()
            msg_type = payload.get("type")

            # ── Cancel / interrupt ────────────────────────────────────────
            if msg_type == "cancel":
                cancelled.set()
                await ws.send_json({"type": "cancelled"})
                continue

            # ── Ping keepalive ────────────────────────────────────────────
            if msg_type == "ping":
                await ws.send_json({"type": "pong"})
                continue

            # ── Audio blob — transcribe → LLM → TTS pipeline ──────────────
            if msg_type == "audio":
                cancelled.clear()  # reset for a fresh utterance

                audio_data = payload.get("data", "")
                if not isinstance(audio_data, str) or not audio_data:
                    await ws.send_json({"type": "error", "message": "Missing audio data"})
                    continue

                # Decode base64 strictly so malformed padding is caught.
                try:
                    raw_bytes = base64.b64decode(audio_data, validate=True)
                except Exception as exc:
                    logger.error(f"Base64 decode error: {exc}")
                    await ws.send_json({"type": "error", "message": f"Bad audio data: {exc}"})
                    continue

                # Transcribe the audio
                try:
                    transcript = whisper.transcribe_bytes(raw_bytes)
                except Exception as exc:
                    logger.error(f"Transcription error: {exc}")
                    await ws.send_json({"type": "error", "message": f"Transcription failed: {exc}"})
                    continue

                # Send the transcribed text to the client
                await ws.send_json({"type": "transcript", "text": transcript})

                # Build LLM messages from the transcript
                llm_messages = [{"role": "user", "content": transcript}]

                provider = payload.get("provider", "openai")
                model = payload.get("model", None)
                base_url = payload.get("base_url", None)
                api_key = payload.get("api_key", None)

                llm_client = LLMClient(
                    provider=provider,
                    model=model,
                    base_url=base_url,
                    api_key=api_key,
                )

                # Stream tokens from the LLM and synthesize each token to audio
                try:
                    async for token in llm_client.generate_stream(llm_messages):
                        if cancelled.is_set():
                            await ws.send_json({"type": "cancelled"})
                            break

                        # Send the raw token to the client (for display/logging)
                        await ws.send_json({"type": "token", "token": token})

                        # Synthesize this token's audio and send it back
                        try:
                            audio_chunk = await tts.synthesize(token)
                            encoded = base64.b64encode(audio_chunk).decode("ascii")
                            await ws.send_json({"type": "audio", "data": encoded})
                        except Exception as exc:
                            logger.error(f"TTS error for token '{token}': {exc}")

                    else:
                        # Loop completed without a break → generation finished normally
                        await ws.send_json({"type": "done"})

                except Exception as exc:
                    logger.error(f"LLM generation error: {exc}")
                    await ws.send_json({"type": "error", "message": f"Generation failed: {exc}"})

    except Exception:
        # WebSocketDisconnect or other fatal errors — exit cleanly
        pass
    finally:
        cancelled.set()
