"""FastAPI application entry point."""

from fastapi import FastAPI
from app.routers import health, chat, rag, summaries

app = FastAPI(title="KotoSensei Backend")

app.include_router(health.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(rag.router, prefix="/api")
app.include_router(summaries.router, prefix="/api")
