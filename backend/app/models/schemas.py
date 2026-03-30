from typing import Literal

from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    query: str
    model: str = "anthropic/claude-sonnet-4-6"
    stream: bool = False
    history: list[ChatMessage] = []


class ChatResponse(BaseModel):
    response: str
    sources: list[str] = []
    model: str


class IngestResponse(BaseModel):
    filename: str
    doc_type: str
    detail: str


class SystemPromptUpdate(BaseModel):
    prompt: str


class SystemPromptResponse(BaseModel):
    prompt: str
