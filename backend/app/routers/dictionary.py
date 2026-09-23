import json
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import or_, String

from app.database import get_db
from app.models import DictionaryEntry
from app.llm import LLMClient
from app.routers.settings import load_settings

router = APIRouter()


class DictionaryAnalyzeRequest(BaseModel):
    kanji: Optional[str] = ""
    reading: Optional[str] = ""
    meanings: List[str] = []


@router.post("/dictionary/analyze")
async def analyze_dictionary_entry(payload: DictionaryAnalyzeRequest):
    """
    Analyze a dictionary entry using LLMClient to return romaji, JLPT level, usage nuance, and an example sentence.
    """
    kanji = payload.kanji or ""
    reading = payload.reading or ""
    meanings = payload.meanings or []

    settings = load_settings()
    provider = settings.get("provider", "local")
    model = settings.get("model", "llama3.2")
    base_url = settings.get("base_url", "http://localhost:11434/v1")
    api_key = settings.get("api_key", "")

    client = LLMClient(
        provider=provider,
        model=model,
        base_url=base_url,
        api_key=api_key if api_key else None,
        timeout=30.0,
    )

    system_prompt = (
        "You are an expert Japanese language teacher. "
        "Analyze the provided Japanese dictionary entry and return a JSON object with no markdown formatting or markdown code blocks.\n"
        "Estimate the jlpt_level based on the kanji, reading, and meanings provided. Provide a natural example sentence in Japanese with pure hiragana reading and English translation.\n"
        "Required JSON schema:\n"
        '{\n'
        '  "romaji": "<romaji pronunciation>",\n'
        '  "jlpt_level": "<e.g. N5, N4, N3, N2, N1>",\n'
        '  "nuance": "<Detailed English explanation of usage nuance, tone, and practical context.>",\n'
        '  "example": {\n'
        '    "japanese": "<Natural Japanese example sentence containing the term>",\n'
        '    "hiragana": "<Full hiragana reading of the Japanese sentence with spaces between words>",\n'
        '    "english": "<Natural English translation of the sentence>"\n'
        '  }\n'
        '}'
    )

    user_prompt = f"Kanji: {kanji}\nReading: {reading}\nMeanings: {', '.join(meanings)}"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    try:
        raw_response = await client.generate_response(messages, temperature=0.2)
        clean_resp = raw_response.strip()
        if clean_resp.startswith("```"):
            lines = clean_resp.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            clean_resp = "\n".join(lines).strip()

        data = json.loads(clean_resp)
        example_data = data.get("example") or {}
        example_obj = None
        if isinstance(example_data, dict) and example_data.get("japanese"):
            example_obj = {
                "japanese": str(example_data.get("japanese", "")),
                "hiragana": str(example_data.get("hiragana", "")),
                "english": str(example_data.get("english", "")),
            }

        return {
            "romaji": data.get("romaji", ""),
            "jlpt_level": data.get("jlpt_level", "N3"),
            "nuance": data.get("nuance", "Common Japanese expression."),
            "example": example_obj,
        }
    except Exception as e:
        return {
            "romaji": reading or "",
            "jlpt_level": "N3",
            "nuance": f"Sensei analysis unavailable ({str(e)})",
            "example": None,
        }


@router.get("/dictionary/search")
def search_dictionary(
    q: Optional[str] = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(30, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Search JMdict dictionary entries in PostgreSQL with optional q filter and pagination.
    """
    search_query = (q or "").strip()

    query = db.query(DictionaryEntry)
    if search_query:
        query = query.filter(
            or_(
                DictionaryEntry.kanji.cast(String).ilike(f"%{search_query}%"),
                DictionaryEntry.reading.cast(String).ilike(f"%{search_query}%"),
                DictionaryEntry.senses.cast(String).ilike(f"%{search_query}%"),
            )
        )

    db_entries = query.offset(offset).limit(limit).all()

    formatted_entries = []
    for entry in db_entries:
        kanji_val = (
            entry.kanji[0]
            if entry.kanji and len(entry.kanji) > 0
            else (entry.reading[0] if entry.reading and len(entry.reading) > 0 else "")
        )
        reading_val = (
            entry.reading[0] if entry.reading and len(entry.reading) > 0 else ""
        )

        meanings = []
        pos_list = []
        examples = []

        if entry.senses:
            for sense in entry.senses:
                if isinstance(sense, dict):
                    glosses = sense.get("glosses") or sense.get("meanings") or []
                    meanings.extend(glosses)
                    parts = sense.get("parts_of_speech") or sense.get("pos") or []
                    for p in parts:
                        if p not in pos_list:
                            pos_list.append(p)
                    exs = sense.get("examples") or []
                    examples.extend(exs)

        item = {
            "id": f"dict-{entry.id}",
            "kanji": kanji_val,
            "reading": reading_val,
            "meanings": meanings or ["Japanese word"],
            "pos": pos_list or ["Noun"],
            "examples": examples,
        }

        formatted_entries.append(item)

    return formatted_entries


