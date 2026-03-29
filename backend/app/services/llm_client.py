from openai import AsyncOpenAI

from app.core.config import settings


class LLMClient:
    def __init__(self) -> None:
        self.client = AsyncOpenAI(
            api_key=settings.openrouter_api_key,
            base_url=settings.llm_base_url,
        )

    async def chat(
        self,
        messages: list[dict],
        model: str,
        tools: list[dict] | None = None,
    ):
        """Non-streaming chat completion. Returns a ChatCompletion object."""
        kwargs: dict = {"model": model, "messages": messages}
        if tools:
            kwargs["tools"] = tools
        return await self.client.chat.completions.create(**kwargs)

    async def chat_stream(
        self,
        messages: list[dict],
        model: str,
        tools: list[dict] | None = None,
    ):
        """Streaming chat completion. Returns an AsyncStream."""
        kwargs: dict = {"model": model, "messages": messages, "stream": True}
        if tools:
            kwargs["tools"] = tools
        return await self.client.chat.completions.create(**kwargs)
