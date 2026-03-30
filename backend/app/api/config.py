from typing import Any

from fastapi import APIRouter

from app.core.config import settings
from app.core.prompt_store import prompt_store
from app.models.schemas import SystemPromptResponse, SystemPromptUpdate

router = APIRouter()


@router.get("/api/config/system-prompt", response_model=SystemPromptResponse)
async def get_system_prompt() -> SystemPromptResponse:
    return SystemPromptResponse(prompt=prompt_store.get_prompt())


@router.put("/api/config/system-prompt", response_model=SystemPromptResponse)
async def update_system_prompt(update: SystemPromptUpdate) -> SystemPromptResponse:
    prompt_store.set_prompt(update.prompt)
    return SystemPromptResponse(prompt=prompt_store.get_prompt())


@router.get("/api/config/models")
async def get_models() -> dict[str, Any]:
    return {
        "models": [
            {
                "id": settings.thinking_model,
                "label": "Thinking Model",
                "type": "thinking",
            },
            {
                "id": settings.non_thinking_model,
                "label": "Standard Model",
                "type": "standard",
            },
        ],
        "default": settings.non_thinking_model,
    }
