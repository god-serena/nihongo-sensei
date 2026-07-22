"""Tests for session summary generation."""

import pytest
from unittest.mock import MagicMock
from app.summaries import generate_summary, SummaryParseError


def test_successful_summary_generation():
    """Test that a valid transcript produces a structured summary."""
    mock_llm = MagicMock()
    mock_llm.generate_response.return_value = (
        '{"topics": ["greetings", "weather"], '
        '"new_vocabulary": [{"term": "こんにちは", "reading": "konnichiwa", "meaning": "hello"}, '
        '{"term": "天気", "reading": "tenki", "meaning": "weather"}], '
        '"mistakes": [{"original": "私は行きます", "correction": "私は行きます", "explanation": "correct usage"}]}'
    )

    messages = [
        {"role": "user", "content": "こんにちは"},
        {"role": "assistant", "content": "こんにちは！"},
    ]

    result = generate_summary(messages, mock_llm)

    assert result["topics"] == ["greetings", "weather"]
    assert len(result["new_vocabulary"]) == 2
    assert len(result["mistakes"]) == 1


def test_summary_parse_error_on_non_json():
    """Test that SummaryParseError is raised when LLM returns non-JSON."""
    mock_llm = MagicMock()
    mock_llm.generate_response.return_value = "not valid json at all"

    messages = [{"role": "user", "content": "hello"}]

    with pytest.raises(SummaryParseError) as exc_info:
        generate_summary(messages, mock_llm)

    assert "Failed to parse LLM response as JSON" in str(exc_info.value)


def test_summary_parse_error_on_missing_keys():
    """Test that SummaryParseError is raised when keys are missing."""
    mock_llm = MagicMock()
    mock_llm.generate_response.return_value = '{"topics": []}'

    messages = [{"role": "user", "content": "hello"}]

    with pytest.raises(SummaryParseError) as exc_info:
        generate_summary(messages, mock_llm)

    assert "Missing keys" in str(exc_info.value)


def test_empty_transcript_produces_valid_empty_summary():
    """Test that an empty transcript produces a valid but empty summary."""
    mock_llm = MagicMock()
    mock_llm.generate_response.return_value = (
        '{"topics": [], "new_vocabulary": [], "mistakes": []}'
    )

    messages: list[dict] = []

    result = generate_summary(messages, mock_llm)

    assert result["topics"] == []
    assert result["new_vocabulary"] == []
    assert result["mistakes"] == []


def test_empty_summary_helper():
    """Test that generate_empty_summary returns a valid empty structure."""
    from app.summaries import generate_empty_summary

    result = generate_empty_summary()

    assert result["topics"] == []
    assert result["new_vocabulary"] == []
    assert result["mistakes"] == []


def test_summary_parse_error_on_invalid_vocab_entry():
    """Test that SummaryParseError is raised when vocabulary entry is invalid."""
    mock_llm = MagicMock()
    mock_llm.generate_response.return_value = (
        '{"topics": [], "new_vocabulary": ["not an object"], "mistakes": []}'
    )

    messages = [{"role": "user", "content": "hello"}]

    with pytest.raises(SummaryParseError) as exc_info:
        generate_summary(messages, mock_llm)

    assert "'new_vocabulary' contains invalid entry" in str(exc_info.value)


def test_summary_parse_error_on_invalid_mistake_entry():
    """Test that SummaryParseError is raised when mistake entry is invalid."""
    mock_llm = MagicMock()
    mock_llm.generate_response.return_value = (
        '{"topics": [], "new_vocabulary": [], "mistakes": ["not an object"]}'
    )

    messages = [{"role": "user", "content": "hello"}]

    with pytest.raises(SummaryParseError) as exc_info:
        generate_summary(messages, mock_llm)

    assert "'mistakes' contains invalid entry" in str(exc_info.value)


def test_summary_parse_error_on_non_dict_response():
    """Test that SummaryParseError is raised when LLM response is not a dict."""
    mock_llm = MagicMock()
    mock_llm.generate_response.return_value = '["just", "a", "list"]'

    messages = [{"role": "user", "content": "hello"}]

    with pytest.raises(SummaryParseError) as exc_info:
        generate_summary(messages, mock_llm)

    assert "LLM response is not a valid object" in str(exc_info.value)


def test_llm_called_with_correct_messages():
    """Test that the LLM client receives both system and user messages."""
    mock_llm = MagicMock()
    mock_llm.generate_response.return_value = '{"topics": [], "new_vocabulary": [], "mistakes": []}'

    messages = [{"role": "user", "content": "test message"}]

    generate_summary(messages, mock_llm)

    call_args = mock_llm.generate_response.call_args[0][0]
    assert len(call_args) == 2
    assert call_args[0]["role"] == "system"
    assert call_args[1]["role"] == "user"
    assert "test message" in call_args[1]["content"]
