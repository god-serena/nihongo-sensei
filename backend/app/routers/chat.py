"""Chat endpoint using LLMClient streaming."""

import json
from typing import AsyncGenerator

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from app.llm import LLMClient

router = APIRouter()


@router.post("/chat")
async def chat(request: Request):
    """Stream tokens back using SSE from the LLM."""
    body = await request.json()

    provider = body.get("provider", "openai")
    model = body.get("model", None)
    base_url = body.get("base_url", None)
    api_key = body.get("api_key", None)
    temperature = body.get("temperature", 0.7)
    messages = body.get("messages", [])

    client = LLMClient(
        provider=provider,
        model=model,
        base_url=base_url,
        api_key=api_key,
        timeout=30.0,
    )

    async def generate_stream():
        async for token in client.generate_stream(messages, temperature):
            yield f"data: {json.dumps({'token': token})}\n\n"

    return StreamingResponse(generate_stream(), media_type="text/event-stream")
