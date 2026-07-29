"""Chat endpoint using LLMClient streaming."""

import json

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from app.llm import LLMClient
from app.routers.settings import load_settings

router = APIRouter()

BILINGUAL_PERSONA = (
    "You are Koto Sensei (琴先生), a warm, bilingual native Japanese teacher who is fluent in English. "
    "Explain grammar and vocabulary in clear, friendly English while providing authentic Japanese phrase demonstrations with furigana brackets 漢字[かんじ]."
    "Strictly do not provide answers unrelated to the Japanese language learning context (e.g., do not answer questions about unrelated topics, personal advice, or general knowledge)."
    "If you already greeted the user, do not greet them again. Instead, continue the conversation naturally"
)

IMMERSION_PERSONA = (
    "You are Koto Sensei (琴先生), a native Japanese teacher conducting a 100% Full Immersion Japanese session (日本語オンリー). "
    "Respond ONLY in natural Japanese. Do NOT use English at all. Use simple Japanese (やさしい日本語) to explain new vocabulary, with furigana brackets 漢字[かんじ]."
    "Strictly do not provide answers unrelated to the Japanese language learning context (e.g., do not answer questions about unrelated topics, personal advice, or general knowledge)."
    "If you already greeted the user, do not greet them again. Instead, continue the conversation naturally"
)

DEFAULT_PERSONA = BILINGUAL_PERSONA


@router.post("/chat")
async def chat(request: Request):
    """Stream tokens back using SSE from the LLM."""
    body = await request.json()
    saved = load_settings()

    provider = body.get("provider") or saved.get("provider", "local")
    model = body.get("model") or saved.get("model", "llama3.2")
    base_url = body.get("base_url") or saved.get("base_url", "http://localhost:11434/v1")
    api_key = body.get("api_key") or saved.get("api_key", "")
    temperature = body.get("temperature", 0.7)
    messages = body.get("messages", [])
    jlpt_level = body.get("jlptLevel", "N4")
    # topic = body.get("topic", "General Practice")
    teaching_mode = body.get("teaching_mode") or "bilingual"

    persona = IMMERSION_PERSONA if teaching_mode == "immersion" else BILINGUAL_PERSONA

    custom_prompt = body.get("custom_system_prompt")
    if custom_prompt is None:
        custom_prompt = saved.get("custom_system_prompt", "")

    system_prompt = (
        f"{persona}\n"
        f"Target Learner JLPT Level: {jlpt_level}.\n"
        # f"Focus Topic: {topic}.\n" //disabled for now
        f"Instruction: Tailor your Japanese vocabulary, grammar complexity, furigana annotations, and explanations to match the {jlpt_level} level."
    )
    if custom_prompt:
        system_prompt += f"\n\nAdditional Instructions:\n{custom_prompt}"

    full_messages = [{"role": "system", "content": system_prompt}] + list(messages)

    client = LLMClient(
        provider=provider,
        model=model,
        base_url=base_url,
        api_key=api_key if api_key else None,
        timeout=30.0,
    )

    async def generate_stream():
        try:
            async for token in client.generate_stream(full_messages, temperature):
                yield f"data: {json.dumps({'token': token})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(generate_stream(), media_type="text/event-stream")

