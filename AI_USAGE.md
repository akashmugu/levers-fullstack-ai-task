# AI Tool Usage Disclosure

## Tools Used

| Tool | Version | Usage |
|------|---------|-------|
| Claude Code (CLI) | Claude Opus 4.6 | Primary development assistant for backend and frontend implementation |

## Scope

AI assistance was used across the full stack:

- **Backend**: FastAPI app structure, RAG engine with agentic tool-calling loop, ChromaDB/DuckDB integration, API endpoints, test suite
- **Frontend**: Next.js 16 app structure, React components, custom hooks, API client, Vitest test suite
- **Documentation**: README, CLAUDE.md, API spec

## Prompts & Design Docs

Key design conversations and prompts are saved in `docs/ai/`:

- [`docs/ai/rag-workflow.md`](docs/ai/rag-workflow.md) — Dynamic tool binding and plan-and-execute RAG workflow design
- [`docs/ai/rag-plan-and-execute-1.md`](docs/ai/rag-plan-and-execute-1.md) — Brainstorm on structured vs unstructured data handling approaches
- [`docs/ai/api-spec.md`](docs/ai/api-spec.md) — API specification developed iteratively
- [`docs/claude_code/1_create_min_be.md`](docs/claude_code/1_create_min_be.md) — Initial backend creation instructions

## Human Review

- All generated code was reviewed for correctness, security (SQL injection protection, input validation), and alignment with project requirements
- Backend tests (49 tests via pytest) validate API contracts, RAG engine logic, chunking, and store operations
- Frontend tests (29 tests via Vitest) validate component rendering, user interactions, and API client behavior
- Linting passes on both backend (ruff) and frontend (ESLint) with zero errors
- Manual testing performed for end-to-end chat flow, document upload/delete, streaming, and model switching

## Understanding

I am prepared to explain all AI-generated code, including:
- The agentic tool-calling RAG pattern and why it was chosen over static retrieve-then-generate
- ChromaDB for vector search vs DuckDB for structured SQL queries
- SSE streaming implementation details
- Dynamic tool binding based on available data sources
