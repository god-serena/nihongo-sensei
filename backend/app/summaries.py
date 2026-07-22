"""Session summary generation using LLM orchestration."""

import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


class SummaryParseError(Exception):
    """Raised when the LLM response cannot be parsed into the expected schema."""

    pass


_SYSTEM_PROMPT = (
    "You are a Japanese language lesson analyst. "
    "Analyze the conversation transcript and "
    "produce a structured JSON summary.\n"
    "Respond ONLY with valid JSON — no markdown fences, no extra text.\n"
    "Use this exact schema:\n"
    '{"topics": ["list of lesson topics covered"], '
    '"new_vocabulary": [{"term": "...", "reading": "...", "meaning": "..."}], '
    '"mistakes": [{"original": "...", "correction": "...", "explanation": "..."}]}'
)


def generate_summary(
    messages: list[dict[str, Any]],
    llm_client: Any,
) -> dict[str, Any]:
    """Generate a structured JSON session summary from a conversation transcript.

    Args:
        messages: List of message dicts (role/content) representing the conversation.
        llm_client: An LLMClient instance with generate_response available.

    Returns:
        A dict matching the expected schema with keys 'topics', 'new_vocabulary', and 'mistakes'.

    Raises:
        SummaryParseError: If the LLM response cannot be parsed or doesn't conform to the schema.
    """
    # Build user message from transcript
    transcript = "\n".join(
        f"[{msg.get('role', 'user')}] {msg.get('content', '')}" for msg in messages
    )

    system_message = {"role": "system", "content": _SYSTEM_PROMPT}
    user_message = {"role": "user", "content": transcript}

    response_text: str = llm_client.generate_response(
        [system_message, user_message], temperature=0.3
    )

    # Parse the JSON response
    try:
        summary = json.loads(response_text)
    except (json.JSONDecodeError, TypeError) as e:
        raise SummaryParseError(f"Failed to parse LLM response as JSON: {e}")

    # Validate schema
    if not isinstance(summary, dict):
        raise SummaryParseError("LLM response is not a valid object")

    expected_keys = {"topics", "new_vocabulary", "mistakes"}
    missing_keys = expected_keys - set(summary.keys())
    if missing_keys:
        raise SummaryParseError(f"Missing keys in summary: {missing_keys}")

    # Validate topics is a list of strings
    if not isinstance(summary["topics"], list):
        raise SummaryParseError("'topics' must be a list")

    # Validate new_vocabulary entries
    for entry in summary.get("new_vocabulary", []):
        if not isinstance(entry, dict) or "term" not in entry:
            raise SummaryParseError(f"'new_vocabulary' contains invalid entry: {entry}")

    # Validate mistakes entries
    for entry in summary.get("mistakes", []):
        if not isinstance(entry, dict) or "original" not in entry:
            raise SummaryParseError(f"'mistakes' contains invalid entry: {entry}")

    return summary


def generate_empty_summary() -> dict[str, Any]:
    """Return an empty but valid summary structure."""
    return {"topics": [], "new_vocabulary": [], "mistakes": []}
