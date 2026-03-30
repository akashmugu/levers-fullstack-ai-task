import type {
  ChatRequest,
  ChatResponse,
  DocumentList,
  ModelsResponse,
  SystemPromptResponse,
  UploadResponse,
} from "@/types";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE_URL}${path}`, options);
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(body?.detail ?? `Request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export async function sendChat(body: ChatRequest): Promise<ChatResponse> {
  return request<ChatResponse>("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ...body, stream: false }),
  });
}

export function streamChat(
  body: ChatRequest,
  onToken: (token: string) => void,
  onSources: (sources: string[]) => void,
  onDone: () => void,
  onError: (error: string) => void,
): AbortController {
  const controller = new AbortController();

  fetch(`${BASE_URL}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ...body, stream: true }),
    signal: controller.signal,
  })
    .then(async (response) => {
      if (!response.ok) {
        const errorBody = await response.json().catch(() => null);
        onError(errorBody?.detail ?? `Request failed: ${response.status}`);
        return;
      }

      const reader = response.body?.getReader();
      if (!reader) {
        onError("No response body");
        return;
      }

      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() ?? "";

        for (const line of lines) {
          const trimmed = line.trim();
          if (!trimmed.startsWith("data: ")) continue;

          const jsonStr = trimmed.slice(6);
          if (!jsonStr) continue;

          try {
            const event = JSON.parse(jsonStr);
            if (event.error) {
              onError(event.error);
              return;
            }
            if (event.token) {
              onToken(event.token);
            }
            if (event.sources) {
              onSources(event.sources);
            }
            if (event.done) {
              onDone();
              return;
            }
          } catch {
            // skip malformed SSE lines
          }
        }
      }

      onDone();
    })
    .catch((err) => {
      if (err instanceof DOMException && err.name === "AbortError") return;
      onError(err instanceof Error ? err.message : "Stream failed");
    });

  return controller;
}

export async function fetchDocuments(): Promise<DocumentList> {
  return request<DocumentList>("/api/documents");
}

export async function uploadDocument(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);
  return request<UploadResponse>("/api/documents", {
    method: "POST",
    body: formData,
  });
}

export async function deleteDocument(
  filename: string,
): Promise<{ detail: string }> {
  return request<{ detail: string }>(`/api/documents/${encodeURIComponent(filename)}`, {
    method: "DELETE",
  });
}

export async function fetchModels(): Promise<ModelsResponse> {
  return request<ModelsResponse>("/api/config/models");
}

export async function fetchSystemPrompt(): Promise<SystemPromptResponse> {
  return request<SystemPromptResponse>("/api/config/system-prompt");
}

export async function updateSystemPrompt(
  prompt: string,
): Promise<SystemPromptResponse> {
  return request<SystemPromptResponse>("/api/config/system-prompt", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt }),
  });
}
