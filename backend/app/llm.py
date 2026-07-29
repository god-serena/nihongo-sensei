import json
import logging
import os
from typing import AsyncIterator, Optional
import httpx

logger = logging.getLogger(__name__)


class LLMClient:
    """
    Unified LLM Client supporting OpenAI-compatible endpoints and native Gemini API.
    """

    def __init__(
        self,
        provider: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: float = 30.0,
    ):
        self.provider = provider.lower()
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.timeout = timeout

        if self.provider in ("openai", "local"):
            # Default to Ollama defaults if base_url is not set
            if not self.base_url:
                self.base_url = "http://localhost:11434/v1"
            # Strip trailing slash if present
            self.base_url = self.base_url.rstrip("/")
            # Ensure base_url ends with /v1 for OpenAI-compatible endpoints
            if not self.base_url.endswith("/v1"):
                self.base_url = f"{self.base_url}/v1"

            is_dev = os.getenv("IS_DEV", "false").lower() in ("true", "1") or os.path.exists("/.dockerenv")
            if is_dev and ("localhost" in self.base_url or "127.0.0.1" in self.base_url):
                self.base_url = self.base_url.replace("localhost", "host.docker.internal").replace("127.0.0.1", "host.docker.internal")
                logger.info(f"Development environment detected: mapped local LLM base_url to {self.base_url}")

            if not self.model:
                self.model = "llama3.2" if self.provider == "local" else "llama3"
        elif self.provider == "gemini":
            if not self.model:
                self.model = "gemini-1.5-flash"
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    async def generate_response(self, messages: list[dict], temperature: float = 0.7) -> str:
        """
        Generate a complete non-streaming response.
        """
        chunks = []
        async for chunk in self.generate_stream(messages, temperature):
            chunks.append(chunk)
        return "".join(chunks)

    async def generate_stream(
        self,
        messages: list[dict],
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        """
        Generate a streaming response, yielding tokens as they arrive.
        """
        if self.provider in ("openai", "local"):
            async for chunk in self._stream_openai(messages, temperature):
                yield chunk
        elif self.provider == "gemini":
            async for chunk in self._stream_gemini(messages, temperature):
                yield chunk

    async def _stream_openai(self, messages: list[dict], temperature: float) -> AsyncIterator[str]:
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "stream": True,
        }

        url = f"{self.base_url}/chat/completions"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                async with client.stream("POST", url, headers=headers, json=payload) as response:
                    if response.status_code != 200:
                        raw_bytes = await response.aread()
                        error_text = raw_bytes.decode('utf-8', errors='ignore')
                        logger.error(
                            f"OpenAI/Local completion failed ({response.status_code}): {error_text}"
                        )
                        err_detail = error_text
                        try:
                            err_json = json.loads(error_text)
                            if isinstance(err_json, dict):
                                err_detail = err_json.get("error", {}).get("message") or err_json.get("error") or error_text
                        except Exception:
                            pass
                        raise RuntimeError(f"Model error ({response.status_code}): {err_detail}")

                    async for line in response.aiter_lines():
                        if not line.strip():
                            continue
                        if line.startswith("data: "):
                            data_str = line[6:].strip()
                            if data_str == "[DONE]":
                                break
                            try:
                                data = json.loads(data_str)
                                choices = data.get("choices", [])
                                if choices:
                                    delta = choices[0].get("delta", {})
                                    content = delta.get("content", "")
                                    if content:
                                        yield content
                            except json.JSONDecodeError:
                                logger.warning(f"Failed to decode SSE line: {line}")
            except httpx.ConnectError as e:
                logger.error(f"Error connecting to LLM server at {self.base_url}: {e}")
                raise RuntimeError(
                    f"Could not connect to LLM server at {self.base_url}. "
                    f"Please check your Settings in KotoSensei and ensure your local LLM (Ollama / LM Studio) or API key is running."
                ) from e
            except Exception as e:
                logger.error(f"Error in OpenAI streaming: {e}")
                raise

    async def _stream_gemini(self, messages: list[dict], temperature: float) -> AsyncIterator[str]:
        if not self.api_key:
            raise ValueError("Gemini API key must be provided.")

        # Prepare Gemini payload
        system_instruction = None
        contents = []

        for msg in messages:
            role = msg.get("role")
            content = msg.get("content", "")
            if role == "system":
                system_instruction = {"parts": [{"text": content}]}
            else:
                gemini_role = "model" if role in ("assistant", "model") else "user"
                contents.append({"role": gemini_role, "parts": [{"text": content}]})

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
            },
        }
        if system_instruction:
            payload["systemInstruction"] = system_instruction

        base = "https://generativelanguage.googleapis.com/v1beta"
        url = f"{base}/models/{self.model}:streamGenerateContent?alt=sse&key={self.api_key}"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                async with client.stream("POST", url, json=payload) as response:
                    if response.status_code != 200:
                        error_text = await response.aread()
                        logger.error(
                            f"Gemini generation failed: "
                            f"{response.status_code} - "
                            f"{error_text.decode('utf-8', errors='ignore')}"
                        )
                        raise RuntimeError(f"Gemini API error: {response.status_code}")

                    async for line in response.aiter_lines():
                        if not line.strip():
                            continue
                        if line.startswith("data: "):
                            data_str = line[6:].strip()
                            try:
                                data = json.loads(data_str)
                                candidates = data.get("candidates", [])
                                if candidates:
                                    content_obj = candidates[0].get("content", {})
                                    parts = content_obj.get("parts", [])
                                    if parts:
                                        text = parts[0].get("text", "")
                                        if text:
                                            yield text
                            except json.JSONDecodeError:
                                logger.warning(f"Failed to decode Gemini SSE line: {line}")
            except Exception as e:
                logger.error(f"Error in Gemini streaming: {e}")
                raise
