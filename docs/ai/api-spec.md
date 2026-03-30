# Backend API Spec

Base URL: `http://localhost:8000`

---

## POST /api/chat

Send a message and get a RAG-augmented response.

Request body (JSON):
```
{ query: string, model: string, stream: boolean, history: {role: "user"|"assistant", content: string}[] }
```
Defaults: `model="anthropic/claude-sonnet-4-6"`, `stream=false`, `history=[]`

**Non-streaming** (`stream: false`): returns JSON:
```
{ response: string, sources: string[], model: string }
```

**Streaming** (`stream: true`): returns `text/event-stream` (SSE). Events:
- `data: {"token": "partial text"}` — append to response
- `data: {"done": true}` — stream complete
- `data: {"error": "message"}` — error occurred

Error: `502` with `{"detail": "..."}` on LLM failure.

---

## GET /api/documents

List all ingested documents.

Response:
```
{ unstructured: string[], structured: string[] }
```
Example: `{ "unstructured": ["fdcpa_quick_reference.md", "glossary.md"], "structured": ["sample_accounts.csv"] }`

---

## POST /api/documents

Upload and ingest a document. Multipart form: field `file`.

Accepted extensions: `.md`, `.csv`, `.txt`

Response:
```
{ filename: string, doc_type: "structured"|"unstructured", detail: string }
```

Error: `400` for unsupported file type.

---

## DELETE /api/documents/{filename}

Delete a document and all its downstream data (vector chunks or DB table + uploaded file).

Response: `{ "detail": "Document '...' deleted" }`

Error: `404` if not found.

---

## GET /api/config/models

List available LLM models.

Response:
```
{ models: {id: string, label: string, type: "thinking"|"standard"}[], default: string }
```

---

## GET /api/config/system-prompt

Response: `{ prompt: string }`

## PUT /api/config/system-prompt

Request body: `{ prompt: string }`
Response: `{ prompt: string }`
