"""Settings endpoint for persistent app configuration."""

import json
from pathlib import Path
from fastapi import APIRouter, Request

router = APIRouter()

SETTINGS_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "settings.json"

DEFAULT_SETTINGS = {
    "provider": "local",
    "base_url": "http://localhost:11434/v1",
    "model": "llama3.2",
    "api_key": "",
    "custom_system_prompt": "",
    "speech_rate": 0.9,
}


def load_settings() -> dict:
    """Load settings from JSON file with fallback to defaults."""
    if SETTINGS_PATH.exists():
        try:
            with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                merged = DEFAULT_SETTINGS.copy()
                merged.update(data)
                return merged
        except Exception:
            pass
    return DEFAULT_SETTINGS.copy()


def save_settings(data: dict) -> dict:
    """Save settings dictionary to JSON file."""
    current = load_settings()
    current.update(data)
    SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(current, f, indent=2)
    return current


@router.get("/settings")
async def get_settings():
    """GET /api/settings returns current configuration."""
    return load_settings()


@router.post("/settings")
async def update_settings(request: Request):
    """POST /api/settings updates configuration in backend/data/settings.json."""
    data = await request.json()
    return save_settings(data)
