import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.llm import LLMClient


@pytest.mark.asyncio
async def test_openai_stream():
    client = LLMClient(
        provider="openai",
        base_url="http://localhost:8000/v1",
        model="test-model",
        api_key="test-key",
    )

    mock_response = MagicMock()
    mock_response.status_code = 200

    async def mock_aiter_lines():
        yield 'data: {"choices": [{"delta": {"content": "Hello"}}]}'
        yield 'data: {"choices": [{"delta": {"content": " world"}}]}'
        yield "data: [DONE]"

    mock_response.aiter_lines = mock_aiter_lines

    mock_stream_ctx = MagicMock()
    mock_stream_ctx.__aenter__ = AsyncMock(return_value=mock_response)
    mock_stream_ctx.__aexit__ = AsyncMock(return_value=None)

    with patch("httpx.AsyncClient.stream", return_value=mock_stream_ctx) as mock_stream:
        response_text = await client.generate_response([{"role": "user", "content": "hi"}])
        assert response_text == "Hello world"

        mock_stream.assert_called_once_with(
            "POST",
            f"{client.base_url}/chat/completions",
            headers={"Authorization": "Bearer test-key"},
            json={
                "model": "test-model",
                "messages": [{"role": "user", "content": "hi"}],
                "temperature": 0.7,
                "stream": True,
            },
        )


@pytest.mark.asyncio
async def test_gemini_stream():
    client = LLMClient(provider="gemini", api_key="gemini-key", model="gemini-1.5-flash")

    mock_response = MagicMock()
    mock_response.status_code = 200

    async def mock_aiter_lines():
        yield 'data: {"candidates": [{"content": {"parts": [{"text": "Konnichiwa"}]}}]}'
        yield 'data: {"candidates": [{"content": {"parts": [{"text": "!"}]}}]}'

    mock_response.aiter_lines = mock_aiter_lines

    mock_stream_ctx = MagicMock()
    mock_stream_ctx.__aenter__ = AsyncMock(return_value=mock_response)
    mock_stream_ctx.__aexit__ = AsyncMock(return_value=None)

    with patch("httpx.AsyncClient.stream", return_value=mock_stream_ctx) as mock_stream:
        response_text = await client.generate_response(
            [
                {"role": "system", "content": "Translate to Japanese"},
                {"role": "user", "content": "hello"},
            ]
        )
        assert response_text == "Konnichiwa!"

        mock_stream.assert_called_once_with(
            "POST",
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:streamGenerateContent?alt=sse&key=gemini-key",
            json={
                "contents": [{"role": "user", "parts": [{"text": "hello"}]}],
                "generationConfig": {"temperature": 0.7},
                "systemInstruction": {"parts": [{"text": "Translate to Japanese"}]},
            },
        )


def test_unsupported_provider():
    with pytest.raises(ValueError):
        LLMClient(provider="unsupported")
