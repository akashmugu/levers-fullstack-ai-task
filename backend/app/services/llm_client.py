from typing import Any

from openai import AsyncOpenAI, AsyncStream
from openai.types.chat import ChatCompletion, ChatCompletionChunk

from app.core.config import settings


class LLMClient:
    def __init__(self) -> None:
        self.client = AsyncOpenAI(
            api_key=settings.openrouter_api_key,
            base_url=settings.llm_base_url,
        )

    async def chat(
        self,
        messages: list[dict[str, Any]],
        model: str,
        tools: list[dict[str, Any]] | None = None,
    ) -> ChatCompletion:
        """Non-streaming chat completion."""
        kwargs: dict[str, Any] = {"model": model, "messages": messages}
        if tools:
            kwargs["tools"] = tools
        return await self.client.chat.completions.create(**kwargs)

    async def chat_stream(
        self,
        messages: list[dict[str, Any]],
        model: str,
        tools: list[dict[str, Any]] | None = None,
    ) -> AsyncStream[ChatCompletionChunk]:
        """Streaming chat completion. Returns an AsyncStream."""
        kwargs: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "stream": True,
        }
        if tools:
            kwargs["tools"] = tools
        return await self.client.chat.completions.create(**kwargs)
