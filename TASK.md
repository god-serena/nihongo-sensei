# KotoSensei (琴先生) - Master Implementation Checklist

> **Agent Instructions:**
> This file is the single source of truth for what to build next. Execute tasks strictly one checkbox at a time, top to bottom, respecting milestone order (later milestones depend on earlier ones).
> Do NOT proceed to the next checkbox until the current task has passing tests (`pytest` for backend, `npm test` → `vitest run` for frontend).
> After a checkbox's tests pass, check it off in this file, then commit to git using: `feat(<task-id>): <short description>` (e.g. `feat(1.4): add SQLAlchemy models`). Bug fixes mid-task use `fix(<task-id>): ...`.
> Any schema change (new/modified table) requires an Alembic migration generated and applied as part of that task — do not hand-edit the DB schema.
> If a task cannot be completed as specified (missing credential, ambiguous requirement, or conflict with `AGENTS.md`), stop and report — do not guess or skip ahead.

---

## Milestone 1: Repository & Backend Core Scaffold
- [x] **1.1 Directory Setup**: Initialize repo structure (`/electron`, `/backend`, `/frontend`, `/data`).
- [x] **1.2 Python Environment**: Create `/backend/requirements.txt` (FastAPI, uvicorn, pytest, sqlalchemy, alembic, psycopg2-binary, pgvector) and set up venv.
- [x] **1.3 Database Compose**: Create `docker-compose.yml` configured for local PostgreSQL with the `pgvector` extension enabled.
- [x] **1.4 DB Models**: Write SQLAlchemy models in `backend/app/models.py` for `Session`, `SessionSummary`, and `Document`. Initialize Alembic (`alembic init`) and generate/apply the initial migration for these tables.
- [x] **1.5 DB Connection Test**: Write a pytest in `backend/tests/test_db.py` to verify PostgreSQL connection, table creation, and CRUD.

---

## Milestone 2: Dictionary Engine (JMdict)
- [x] **2.1 Provider Interface**: Create abstract base class `DictionaryProvider` in `backend/app/dictionaries/base.py` defining `lookup(term: str) -> dict`.
- [x] **2.2 JMdict Parser CLI**: Add `DictionaryEntry` model to `backend/app/models.py`, generate/apply the Alembic migration for it, then create ingestion script `backend/app/ingest_dictionary.py` to parse JMdict XML and populate `dictionary_entries` in Postgres.
- [x] **2.3 JMdict Lookups**: Implement `JMdictProvider` class in `backend/app/dictionaries/jmdict.py`.
- [x] **2.4 Dictionary Unit Tests**: Write pytest in `backend/tests/test_dictionary.py` validating exact-match lookups for Japanese terms (e.g., "日本語", "琴").

---

## Milestone 3: RAG & Vector Pipeline
- [x] **3.1 Chunking Utility**: Write document loader and recursive text splitter in `backend/app/rag.py`.
- [x] **3.2 Embedding Generation**: Implement local HuggingFace embedding generator interface using `nomic-embed-text` or similar lightweight model.
- [x] **3.3 pgvector Storage**: Add a `DocumentChunk` model (with `pgvector` embedding column) to `backend/app/models.py`, generate/apply the Alembic migration, then write functions to store and query document chunks with vector similarity in Postgres via `pgvector`.
- [x] **3.4 RAG Unit Tests**: Write pytest in `backend/tests/test_rag.py` to test document ingestion and similarity retrieval.


---

## Milestone 4: FastAPI Router & LLM Orchestrator
- [x] **4.1 Unified LLM Client**: Create `backend/app/llm.py` supporting OpenAI-compatible endpoints (LM Studio, Ollama) and Gemini API.
- [x] **4.2 Session Summaries**: Write LLM prompt and JSON parser in `backend/app/summaries.py` to generate structured session summaries.
- [x] **4.3 API Endpoints**: Implement FastAPI routes in modular router files under `backend/app/routers/` (`health.py`, `chat.py`, `rag.py`, `summaries.py`) exposing `/api/health`, `/api/chat`, `/api/rag/upload`, `/api/summaries`. `backend/app/main.py` only imports and registers these via `app.include_router()` — no route logic directly in `main.py`.
- [x] **4.4 API Integration Tests**: Write pytest in `backend/tests/test_api.py` testing FastAPI endpoints using `httpx.AsyncClient`.

---

## Milestone 5: Audio & Speech Pipeline
- [x] **5.1 STT Integration**: Implement local Whisper (`faster-whisper`) transcriber in `backend/app/tts_stt.py`.
- [ ] **5.2 TTS Integration**: Implement VOICEVOX / Edge-TTS audio generator.
- [ ] **5.3 WebSocket Engine**: Implement `/ws/speech` websocket endpoint supporting real-time audio streaming, token delivery, and immediate `cancel` (barge-in) messages.

---

## Milestone 6: Vue 3 Frontend (Renderer)
- [ ] **6.1 Vue 3 Setup**: Initialize Vue 3 (Composition API) + Vite + Tailwind CSS in `/frontend`.
- [ ] **6.2 Audio Visualizer**: Build `VoiceVisualizer.vue` for real-time mic waveform display.
- [ ] **6.3 Chat & Controls**: Build `ChatArea.vue` supporting chat history, audio play/pause, and push-to-talk interrupt button.
- [ ] **6.4 RAG & Summary Dashboard**: Build `DocumentManager.vue` and `SessionSummaries.vue`.
- [ ] **6.5 Frontend Unit Tests**: Set up Vitest and write component tests for UI components and WebSocket state handling.

---

## Milestone 7: Electron Integration & Packaging
- [ ] **7.1 Electron Shell**: Initialize Electron main process in `/electron/main.js` to manage main window and preload script.
- [ ] **7.2 Sidecar Management**: Add process spawner in Electron main process to spawn `pyinstaller`-packaged FastAPI backend on startup and kill on exit.
- [ ] **7.3 Packaging Configuration**: Configure `electron-builder` in `package.json` for Windows NSIS builds.