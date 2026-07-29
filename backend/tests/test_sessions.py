"""Tests for session CRUD endpoints."""

import pytest
from starlette.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models import Session as SessionModel


@pytest.fixture()
def client():
    """Return a TestClient."""
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture()
def db_session():
    """Yield a clean database session with no sessions."""
    db = SessionLocal()
    try:
        db.query(SessionModel).delete()
        db.commit()
        yield db
    finally:
        db.close()


@pytest.fixture()
def sample_session(db_session):
    """Create and return a sample session."""
    s = SessionModel(title="New Practice", messages=[], jlpt_level="N4", teaching_mode="bilingual")
    db_session.add(s)
    db_session.commit()
    db_session.refresh(s)
    return s


# ── GET /api/sessions ────────────────────────────────────────────────────────


def test_list_sessions_empty(client):
    """GET /api/sessions returns empty list when no sessions exist."""
    response = client.get("/api/sessions")
    assert response.status_code == 200
    assert response.json() == []


def test_list_sessions_returns_sessions(client, sample_session):
    """GET /api/sessions returns sessions ordered by updated_at desc."""
    response = client.get("/api/sessions")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "New Practice"
    assert data[0]["messages"] == []
    assert data[0]["jlpt_level"] == "N4"
    assert data[0]["teaching_mode"] == "bilingual"


# ── POST /api/sessions ───────────────────────────────────────────────────────


def test_create_session(client, db_session):
    """POST /api/sessions creates a new session and returns it."""
    response = client.post("/api/sessions", json={})
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "New Practice"
    assert data["messages"] == []
    assert data["jlpt_level"] == "N4"
    assert data["teaching_mode"] == "bilingual"

    # Verify it persisted
    row = db_session.query(SessionModel).filter_by(id=data["id"]).first()
    assert row is not None
    assert row.title == "New Practice"


def test_create_session_with_payload(client, db_session):
    """POST /api/sessions respects provided fields."""
    response = client.post("/api/sessions", json={"title": "Kanji Practice"})
    assert response.status_code == 201
    assert response.json()["title"] == "Kanji Practice"


# ── GET /api/sessions/{id} ──────────────────────────────────────────────────


def test_get_session(client, sample_session):
    """GET /api/sessions/{id} returns the session."""
    response = client.get(f"/api/sessions/{sample_session.id}")
    assert response.status_code == 200
    assert response.json()["title"] == "New Practice"


def test_get_session_not_found(client):
    """GET /api/sessions/{id} returns 404 for nonexistent session."""
    response = client.get("/api/sessions/9999")
    assert response.status_code == 404


# ── PUT /api/sessions/{id} ──────────────────────────────────────────────────


def test_update_session(client, sample_session):
    """PUT /api/sessions/{id} updates the session."""
    payload = {
        "title": "Updated Title",
        "messages": [{"role": "user", "content": "こんにちは"}],
        "jlpt_level": "N3",
    }
    response = client.put(f"/api/sessions/{sample_session.id}", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["messages"] == [{"role": "user", "content": "こんにちは"}]
    assert data["jlpt_level"] == "N3"


def test_update_session_not_found(client):
    """PUT /api/sessions/{id} returns 404 for nonexistent session."""
    response = client.put("/api/sessions/9999", json={"title": "x"})
    assert response.status_code == 404


# ── DELETE /api/sessions/{id} ────────────────────────────────────────────────


def test_delete_session(client, sample_session):
    """DELETE /api/sessions/{id} removes the session."""
    response = client.delete(f"/api/sessions/{sample_session.id}")
    assert response.status_code == 204

    # Verify it's gone
    response2 = client.get(f"/api/sessions/{sample_session.id}")
    assert response2.status_code == 404


def test_delete_session_not_found(client):
    """DELETE /api/sessions/{id} returns 404 for nonexistent session."""
    response = client.delete("/api/sessions/9999")
    assert response.status_code == 404
