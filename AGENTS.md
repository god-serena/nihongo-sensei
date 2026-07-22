# AGENTS.md — KotoSensei (琴先生) Development Protocol

## 1. Project Context & Goals
KotoSensei is a local, voiced Japanese language teacher desktop app.
- **Architecture**: Electron desktop shell + FastAPI Python sidecar + Vue 3 frontend + PostgreSQL (`pgvector` extension — no separate vector DB service).
- **Core Features**: Local/frontier LLM orchestration, RAG document search, JMdict dictionary lookups (pluggable per language), structured session summaries, interruptible (barge-in) audio/speech streaming.
- **Deployment model**: local-first, single-user. No hosting costs beyond optional frontier LLM API usage.

---

## 2. Tech Stack & Directory Standards
Maintain strict separation across the codebase layers:

- **Backend (`/backend`)**:
  - Python 3.12, FastAPI, SQLAlchemy (async/sync), Alembic, `pgvector`, `psycopg2-binary`.
  - *(Pin Python 3.12 rather than latest — audio/ML deps like `faster-whisper` typically lag newest Python releases on wheel support. Revisit if confirmed compatible.)*
  - All database models MUST live in `backend/app/models.py`.
  - External language dictionaries live in `backend/app/dictionaries/` behind the shared `DictionaryProvider` interface (`base.py` + `registry.py`) — exact-match lookups, kept separate from RAG's embedding search. New languages plug in here without touching `rag.py`.
  - API endpoints MUST be defined inside modular router files under `backend/app/routers/` (e.g., `routers/chat.py`, `routers/rag.py`, `routers/dictionary.py`).
  - `backend/app/main.py` MUST NOT declare route logic directly; it should only import and register routers via `app.include_router()`.
  - LLM providers (Ollama, LM Studio, Gemini, OpenAI) live behind the unified interface in `backend/app/llm.py`. New providers extend this — never add one-off call sites elsewhere.
  - Session summaries (`summaries.py`) are always structured JSON (topics, new vocab, mistakes) — never a raw transcript dump.
  - Websocket protocol: every message type is designed alongside a `cancel` handler. Barge-in (interrupting TTS mid-response) is a first-class concern; current implementation is push-to-talk (V1), not VAD-based auto-interrupt — don't assume the latter exists.

- **Frontend (`/frontend`)**:
  - Vue 3 using **Composition API with `<script setup>` syntax only**.
  - Vite, Tailwind CSS, Pinia (state management).
  - **Centralized API Client**: All frontend API calls MUST use a centralized client module in `frontend/src/services/api.js`. Never write raw `fetch()` or `axios` calls directly inside `.vue` components.
  - **Testing**: Vitest (not Jest) — `package.json`'s `"test"` script must point to `vitest run`. Vitest was chosen specifically because it shares Vite's config/transforms, so `.vue` SFCs need no extra transform setup. Every component under `src/components/` gets a matching spec under `tests/components/`.

- **Desktop Shell (`/electron`)**:
  - Electron main process (`electron/main.js`) handles window creation and spawns/manages the FastAPI sidecar binary (packaged via `pyinstaller`), including clean shutdown on quit.
  - Renderer has no direct DB or filesystem access — talks to the backend only via the documented HTTP/WebSocket API.

---

## 3. Strict Execution Guardrails

1. **Task Scope Lock**:
   - `TASK.md` (repo root) is a milestone checklist, and the single source of truth for what to build. "The current task" means **the first unchecked box, top to bottom, respecting milestone order** — never jump ahead to a later milestone or a later checkbox within the current one.
   - Execute **ONLY** that one checkbox. Never write boilerplate for future milestones ahead of schedule.
   - When a checkbox's tests pass, check it off in `TASK.md` and commit (`feat(<task-id>): <description>`) before moving to the next box — don't batch multiple checkboxes into one uncommitted pass.

2. **Test-Driven First (TDD)**:
   - Every feature must have a corresponding test.
   - Run `pytest` inside `/backend` for backend changes.
   - Run `npm test` (→ `vitest run`) inside `/frontend` for UI component changes.
   - Never mark a task as complete in `TASK.md` if tests are failing.

3. **Database & Migrations**:
   - Postgres runs locally via `docker-compose.yml` on port `5432`, using the `pgvector/pgvector:pg16` image (or equivalent extension-enabled Postgres) — this single instance serves both relational data and vector search, there is no separate Chroma/vector service.
   - Schema changes go through Alembic migrations, never manual `ALTER TABLE` or hand-edited schema.
   - Use environment variables for DB parameters; do not hardcode passwords in `.py` files.

4. **Error Recovery & Terminal Loop**:
   - If a test fails after running commands, inspect `stdout`/`stderr` logs, correct the implementation, and re-run the suite automatically.
   - Do not request human intervention for minor syntax or import errors — fix them inside the loop.
   - If the same failure recurs after 3 consecutive fix attempts, stop and escalate rather than continuing to guess (see the `/autonomous-task` prompt template for the full escalation protocol).

---