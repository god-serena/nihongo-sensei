"""FastAPI application entry point."""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.database import engine
from app.models import Base
from app.routers import health, chat, rag, summaries, speech, settings, sessions, dictionary

# Ensure pgvector extension and all database tables exist in PostgreSQL
try:
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        conn.commit()
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Warning: DB init / Base.metadata.create_all error: {e}")

app = FastAPI(title="KotoSensei Backend")

raw_origins = os.getenv("ALLOWED_ORIGINS", "*")
allowed_origins = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(settings.router, prefix="/api")
app.include_router(rag.router, prefix="/api")
app.include_router(summaries.router, prefix="/api")
app.include_router(speech.router, prefix="/api")
app.include_router(speech.router)
app.include_router(sessions.router, prefix="/api")
app.include_router(dictionary.router, prefix="/api")


