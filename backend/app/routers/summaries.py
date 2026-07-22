"""Session summaries endpoint."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.summaries import generate_summary
from app.llm import LLMClient
from app.models import SessionSummary


router = APIRouter()


@router.post("/summaries")
async def create_summary(
    payload: dict,
    db: Session = Depends(get_db),
):
    """Generate a structured summary for a session and persist it."""
    session_id = payload.get("session_id")
    messages = payload.get("messages", [])

    provider = payload.get("provider", "openai")
    model = payload.get("model", None)
    base_url = payload.get("base_url", None)
    api_key = payload.get("api_key", None)

    llm_client = LLMClient(
        provider=provider,
        model=model,
        base_url=base_url,
        api_key=api_key,
        timeout=30.0,
    )

    summary_data = generate_summary(messages, llm_client)

    summary_record = SessionSummary(session_id=session_id, summary_data=summary_data)
    db.add(summary_record)
    db.commit()
    db.refresh(summary_record)

    return {"summary_id": summary_record.id, "summary": summary_data}
