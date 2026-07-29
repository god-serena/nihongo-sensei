"""WebSocket speech endpoint — real-time audio streaming with cancel support."""

import asyncio
import base64
import logging

from fastapi import APIRouter, Request, WebSocket

from app.llm import LLMClient
from app.routers.settings import load_settings
from app.tts_stt import TTSGenerator, WhisperTranscriber

logger = logging.getLogger(__name__)

router = APIRouter()

BILINGUAL_PERSONA = (
    "You are Koto Sensei (琴先生), a warm, bilingual native Japanese teacher who is fluent in English. "
    "Explain grammar and vocabulary in clear, friendly English while providing authentic Japanese phrase demonstrations with furigana brackets 漢字[かんじ]."
)

IMMERSION_PERSONA = (
    "You are Koto Sensei (琴先生), a native Japanese teacher conducting a 100% Full Immersion Japanese session (日本語オンリー). "
    "Respond ONLY in natural Japanese. Do NOT use English at all. Use simple Japanese (やさしい日本語) to explain new vocabulary, with furigana brackets 漢字[かんじ]."
)

DEFAULT_PERSONA = BILINGUAL_PERSONA


@router.post("/transcribe")
async def transcribe_audio(request: Request):
    """Transcribe base64 audio bytes using local Whisper model."""
    body = await request.json()
    audio_data = body.get("data", "")
    if not audio_data:
        return {"error": "Missing audio data", "text": ""}

    try:
        raw_bytes = base64.b64decode(audio_data)
        whisper = WhisperTranscriber()
        transcript = whisper.transcribe_bytes(raw_bytes)
        logger.info(f"Whisper STT transcribed: '{transcript}'")
        return {"text": transcript}
    except Exception as e:
        logger.error(f"STT Whisper error: {e}")
        return {"error": str(e), "text": ""}


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

                # Build system prompt with persona and JLPT targeting
                jlpt_level = payload.get("jlptLevel", "N4")
                topic = payload.get("topic", "General Practice")
                custom_prompt = payload.get("custom_system_prompt", "")
                teaching_mode = payload.get("teachingMode") or payload.get("teaching_mode") or "bilingual"

                persona = IMMERSION_PERSONA if teaching_mode == "immersion" else BILINGUAL_PERSONA

                system_prompt = (
                    f"{persona}\n"
                    f"Target Learner JLPT Level: {jlpt_level}.\n"
                    f"Focus Topic: {topic}.\n"
                    f"Instruction: Tailor your Japanese vocabulary, grammar complexity, furigana annotations, and explanations to match the {jlpt_level} level."
                )
                if custom_prompt:
                    system_prompt += f"\n\nAdditional Instructions:\n{custom_prompt}"

                llm_messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": transcript},
                ]

                saved = load_settings()
                provider = payload.get("provider") or saved.get("provider", "local")
                model = payload.get("model") or saved.get("model", "llama3.2")
                base_url = payload.get("base_url") or saved.get("base_url", "http://localhost:11434/v1")
                api_key = payload.get("api_key") or saved.get("api_key", "")

                llm_client = LLMClient(
                    provider=provider,
                    model=model,
                    base_url=base_url,
                    api_key=api_key if api_key else None,
                )

                # Stream tokens from the LLM without TTS synthesis (TTS disabled per user directive)
                try:
                    async for token in llm_client.generate_stream(llm_messages):
                        if cancelled.is_set():
                            await ws.send_json({"type": "cancelled"})
                            break

                        # Send raw token to client for live text typing display
                        await ws.send_json({"type": "token", "token": token})

                    if not cancelled.is_set():
                        await ws.send_json({"type": "done"})

                except Exception as exc:
                    logger.error(f"LLM generation error: {exc}")
                    await ws.send_json({"type": "error", "message": f"Generation failed: {exc}"})

    except Exception:
        # WebSocketDisconnect or other fatal errors — exit cleanly
        pass
    finally:
        cancelled.set()
