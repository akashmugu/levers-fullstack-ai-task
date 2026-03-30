# Frontend — Next.js 16 / React 19

Chat interface for the Debt Collection Compliance Assistant.

## Setup

```bash
npm install
cp .env.example .env.local
npm run dev
```

App runs at http://localhost:3000. Requires the backend at `NEXT_PUBLIC_API_URL` (default: `http://localhost:8000`).

## Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Development server |
| `npm run build` | Production build |
| `npm run lint` | ESLint |
| `npm test` | Vitest test suite |

## Architecture

- **App Router** (`app/`) — Single-page chat layout
- **Components** (`components/`) — ChatMessage, ChatInput, DocumentPanel, ModelSelector, StreamToggle, SystemPromptEditor, EmptyState
- **Hooks** (`hooks/`) — `useChat` (message state + SSE), `useDocuments` (upload/list/delete), `useModels` (model fetching)
- **API Client** (`lib/api.ts`) — Typed fetch wrapper for all backend endpoints
- **Types** (`types/`) — Shared TypeScript interfaces

## Key Dependencies

- `react-markdown` + `remark-gfm` for rendering assistant responses
- `@tailwindcss/typography` for prose styling
- Tailwind CSS v4 with dark mode support
