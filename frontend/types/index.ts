export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: string[];
}

export interface ChatRequest {
  query: string;
  model: string;
  stream: boolean;
  history: Pick<ChatMessage, "role" | "content">[];
}

export interface ChatResponse {
  response: string;
  sources: string[];
  model: string;
}

export interface StreamEvent {
  token?: string;
  done?: boolean;
  sources?: string[];
  error?: string;
}

export interface DocumentList {
  unstructured: string[];
  structured: string[];
}

export interface UploadResponse {
  filename: string;
  doc_type: "structured" | "unstructured";
  detail: string;
}

export interface ModelInfo {
  id: string;
  label: string;
  type: "thinking" | "standard";
}

export interface ModelsResponse {
  models: ModelInfo[];
  default: string;
}

export interface SystemPromptResponse {
  prompt: string;
}
