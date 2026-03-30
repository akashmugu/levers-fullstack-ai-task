# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Full-stack AI chat application for a debt collection agent compliance assistant. Uses a RAG pipeline (vector search + SQL) to ground LLM answers in uploaded documents. Monorepo with a Python/FastAPI backend and a Next.js 16/React 19 frontend.

## Commands

### Backend (from `backend/`)

```bash
# Setup
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # then set OPENROUTER_API_KEY

# Run dev server
uvicorn app.main:app --reload --port 8000

# Swagger docs at http://localhost:8000/docs
```

### Frontend (from `frontend/`)

```bash
npm install
cp .env.example .env.local

npm run dev      # dev server on http://localhost:3000
npm run build    # production build
npm run lint     # ESLint
```

### No test framework is set up yet in either backend or frontend.

## Architecture

### Backend (`backend/app/`)

FastAPI app initialized in `main.py`. Services are instantiated at module level and attached to `app.state` for access in route handlers.

**Request flow for chat:**
1. `api/chat.py` receives `ChatRequest` (query, model, stream flag, history)
2. `services/rag_engine.py` orchestrates a **tool-calling loop** (max 10 iterations):
   - Dynamically binds tools based on what data is available (vector store, structured store)
   - `vector_search` tool: similarity search via ChromaDB for markdown/text documents
   - `sql_query` tool: DuckDB SQL queries for CSV/structured data
3. Streaming responses use SSE via `sse-starlette`; non-streaming returns a full JSON response

**Key services:**
- `services/rag_engine.py` — Core RAG orchestration with agentic tool-calling loop
- `services/vector_store.py` — ChromaDB wrapper (persisted to `./data/chroma/`)
- `services/structured_store.py` — DuckDB wrapper (persisted to `./data/structured.duckdb`)
- `services/llm_client.py` — OpenRouter API client
- `core/prompt_store.py` — In-memory system prompt, updatable at runtime via API
- `core/config.py` — `pydantic-settings` config loaded from `.env`

**Document ingestion:** `api/documents.py` handles uploads. `.md`/`.txt` files are chunked (`utils/chunking.py`) and stored in ChromaDB. `.csv` files are loaded as DuckDB tables.

**LLM models** are configured via env vars (`THINKING_MODEL`, `NON_THINKING_MODEL`) and accessed through OpenRouter.

### Frontend (`frontend/`)

Next.js 16 App Router with React 19. Tailwind CSS v4 for styling.

**Important:** This uses Next.js 16 which has breaking changes from earlier versions. Before writing frontend code, read `node_modules/next/dist/docs/` for current API conventions.

**State management** is handled by custom hooks (no external state library):
- `hooks/useChat.ts` — Chat messages, streaming SSE parsing, send/receive logic
- `hooks/useDocuments.ts` — Document upload, list, delete
- `hooks/useModels.ts` — Available model fetching

**API client** in `lib/api.ts` wraps `fetch()` with the base URL from `NEXT_PUBLIC_API_URL`.

### API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/chat` | Chat query (streaming or non-streaming) |
| POST | `/api/documents` | Upload document (.md, .csv, .txt) |
| GET | `/api/documents` | List ingested documents |
| DELETE | `/api/documents/{filename}` | Delete document |
| GET | `/api/config/system-prompt` | Get system prompt |
| PUT | `/api/config/system-prompt` | Update system prompt |
| GET | `/api/config/models` | List available models |
| GET | `/health` | Health check |

### SSE Streaming Format

```json
{"token": "partial text"}
{"done": true}
{"error": "message"}
```

## Environment Variables

**Backend** (`.env` in `backend/`): `OPENROUTER_API_KEY` (required), `LLM_BASE_URL`, `THINKING_MODEL`, `NON_THINKING_MODEL`, `DATA_DIR`

**Frontend** (`.env.local` in `frontend/`): `NEXT_PUBLIC_API_URL` (defaults to `http://localhost:8000`)

## Reference Data

Seed documents in `rag-reference-data/` for testing the RAG pipeline: FDCPA compliance rules, call scripts, sample accounts CSV, and a glossary. These must be uploaded through the UI or API to be ingested.
