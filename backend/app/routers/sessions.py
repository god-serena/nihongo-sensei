"""Chat session CRUD endpoints."""

import datetime
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Session as SessionModel

router = APIRouter()


def get_db():
    """Yield a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _session_lightweight(session: SessionModel) -> dict:
    """Return a lightweight session dict (no messages array) for list views."""
    return {
        "id": session.id,
        "title": session.title,
        "message_count": len(session.messages or []),
        "jlpt_level": session.jlpt_level,
        "teaching_mode": session.teaching_mode,
        "created_at": session.created_at.isoformat() if session.created_at else None,
        "updated_at": session.updated_at.isoformat() if session.updated_at else None,
    }


def _session_to_dict(session: SessionModel) -> dict:
    """Convert a Session ORM object to a plain dict for JSON serialization."""
    return {
        "id": session.id,
        "title": session.title,
        "messages": session.messages or [],
        "jlpt_level": session.jlpt_level,
        "teaching_mode": session.teaching_mode,
        "created_at": session.created_at.isoformat() if session.created_at else None,
        "updated_at": session.updated_at.isoformat() if session.updated_at else None,
    }


# ── Routes ───────────────────────────────────────────────────────────────────


@router.get("/sessions")
async def list_sessions():
    """GET /api/sessions — List all sessions ordered by updated_at desc."""
    db = SessionLocal()
    try:
        rows = db.query(SessionModel).order_by(
            SessionModel.updated_at.desc()
        ).all()
        return [_session_lightweight(r) for r in rows]
    finally:
        db.close()


@router.post("/sessions", status_code=201)
async def create_session(payload: dict = None):
    """POST /api/sessions — Create a new session."""
    db = SessionLocal()
    try:
        session = SessionModel(
            title=(payload or {}).get("title", "New Practice"),
            messages=(payload or {}).get("messages", []),
            jlpt_level=(payload or {}).get("jlpt_level", "N4"),
            teaching_mode=(payload or {}).get("teaching_mode", "bilingual"),
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return _session_to_dict(session)
    finally:
        db.close()


@router.get("/sessions/{session_id}")
async def get_session(session_id: int):
    """GET /api/sessions/{id} — Get a single session."""
    db = SessionLocal()
    try:
        session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return _session_to_dict(session)
    finally:
        db.close()


@router.put("/sessions/{session_id}")
async def update_session(session_id: int, payload: dict):
    """PUT /api/sessions/{id} — Update session title, messages, or settings."""
    db = SessionLocal()
    try:
        session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        if "title" in payload:
            session.title = payload["title"]
        if "messages" in payload:
            session.messages = payload["messages"]
        if "jlpt_level" in payload:
            session.jlpt_level = payload["jlpt_level"]
        if "teaching_mode" in payload:
            session.teaching_mode = payload["teaching_mode"]

        db.commit()
        db.refresh(session)
        return _session_to_dict(session)
    finally:
        db.close()


@router.delete("/sessions/{session_id}", status_code=204)
async def delete_session(session_id: int):
    """DELETE /api/sessions/{id} — Delete a session."""
    db = SessionLocal()
    try:
        session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        db.delete(session)
        db.commit()
    finally:
        db.close()
