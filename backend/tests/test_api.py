"""Integration tests for FastAPI endpoints using httpx TestClient."""

import pytest
from unittest.mock import MagicMock, patch
from starlette.testclient import TestClient
from app.main import app
from app.database import get_db


# ── Fixtures ───────────────────────────────────────────────────────────────────


@pytest.fixture()
def client():
    """Return a TestClient that does NOT re-raise server-side exceptions."""
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture()
def mock_db_session():
    """A MagicMock that satisfies the SQLAlchemy Session interface."""
    session = MagicMock()

    # Make refresh() assign an id to the object passed in
    def _refresh(obj):
        if not hasattr(obj, "id") or obj.id is None:
            obj.id = 1

    session.refresh.side_effect = _refresh
    return session


@pytest.fixture(autouse=False)
def override_db(mock_db_session):
    """Override the get_db FastAPI dependency with a mock session."""
    app.dependency_overrides[get_db] = lambda: mock_db_session
    yield mock_db_session
    app.dependency_overrides.clear()


# ── GET /api/health ────────────────────────────────────────────────────────────


def test_health_check(client):
    """GET /api/health returns 200 with the expected status JSON."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "kotosensei-backend"


# ── POST /api/chat ─────────────────────────────────────────────────────────────


def test_chat_streaming(client):
    """POST /api/chat streams SSE tokens back from the LLM."""

    # generate_stream must be an async generator function, not a coroutine.
    async def fake_stream(messages, temperature=0.7):
        yield "Hello"
        yield " world"

    with patch("app.routers.chat.LLMClient") as MockLLM:
        instance = MagicMock()
        instance.generate_stream = fake_stream
        MockLLM.return_value = instance

        response = client.post(
            "/api/chat",
            json={
                "provider": "openai",
                "messages": [{"role": "user", "content": "hello"}],
                "temperature": 0.7,
            },
        )

    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]
    # Confirm both tokens appear in the SSE body
    body = response.text
    assert '"Hello"' in body
    assert '" world"' in body


def test_chat_unsupported_provider(client):
    """POST /api/chat with an unsupported provider returns a server error."""
    # LLMClient raises ValueError in __init__ for unknown providers.
    # TestClient (raise_server_exceptions=False) converts unhandled exceptions to 500.
    with patch("app.routers.chat.LLMClient") as MockLLM:
        MockLLM.side_effect = ValueError("Unsupported provider: unknown_llm")

        response = client.post(
            "/api/chat",
            json={
                "provider": "unknown_llm",
                "messages": [{"role": "user", "content": "hello"}],
            },
        )

    assert response.status_code == 500


# ── POST /api/rag/upload ───────────────────────────────────────────────────────


def test_rag_upload(client, override_db):
    """POST /api/rag/upload chunks, embeds and stores a document."""
    with (
        patch("app.routers.rag.load_document", return_value="Hello world"),
        patch("app.routers.rag.RecursiveCharacterTextSplitter") as MockSplitter,
        patch("app.routers.rag.EmbeddingGenerator") as MockGen,
        patch("app.rag.store_document_chunks"),
    ):
        mock_splitter = MagicMock()
        mock_splitter.split_text.return_value = ["chunk1", "chunk2"]
        MockSplitter.return_value = mock_splitter

        mock_gen_instance = MagicMock()
        mock_gen_instance.generate_embeddings.return_value = [[0.1] * 384, [0.1] * 384]
        MockGen.return_value = mock_gen_instance

        response = client.post(
            "/api/rag/upload",
            files={"file": ("test.txt", b"Hello world", "text/plain")},
        )

    assert response.status_code == 200
    data = response.json()
    assert "document_id" in data
    assert "chunk_count" in data
    assert data["chunk_count"] == 2


def test_rag_upload_unsupported_type(client):
    """POST /api/rag/upload with an unsupported file type returns a server error."""
    # load_document raises ValueError for .csv — TestClient maps it to 500.
    response = client.post(
        "/api/rag/upload",
        files={"file": ("test.csv", b"a,b,c", "text/csv")},
    )
    assert response.status_code == 500


# ── POST /api/summaries ────────────────────────────────────────────────────────


def test_summaries_create(client, override_db):
    """POST /api/summaries generates and persists a structured summary."""
    with patch("app.routers.summaries.generate_summary") as mock_gen:
        mock_gen.return_value = {
            "topics": ["greetings"],
            "new_vocabulary": [],
            "mistakes": [],
        }

        response = client.post(
            "/api/summaries",
            json={
                "session_id": 1,
                "messages": [{"role": "user", "content": "hello"}],
                "provider": "openai",
            },
        )

    assert response.status_code == 200
    data = response.json()
    assert "summary_id" in data
    assert "summary" in data
    assert data["summary"]["topics"] == ["greetings"]


def test_summaries_parse_error(client, override_db):
    """POST /api/summaries returns a server error when the LLM output is malformed."""
    from app.summaries import SummaryParseError

    # Patch at the import site (app.routers.summaries), not the definition site.
    with patch("app.routers.summaries.generate_summary") as mock_gen:
        mock_gen.side_effect = SummaryParseError("Bad JSON")

        response = client.post(
            "/api/summaries",
            json={
                "session_id": 1,
                "messages": [{"role": "user", "content": "hello"}],
                "provider": "openai",
            },
        )

    assert response.status_code == 500
