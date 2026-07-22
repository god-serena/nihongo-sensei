"""Health check endpoint."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    """Return a simple liveness/readiness JSON response."""
    return {"status": "ok", "service": "kotosensei-backend"}
