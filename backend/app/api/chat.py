import json

from fastapi import APIRouter, HTTPException, Request
from sse_starlette.sse import EventSourceResponse

from app.models.schemas import ChatRequest, ChatResponse

router = APIRouter()


@router.post("/api/chat")
async def chat(chat_request: ChatRequest, request: Request):
    engine = request.app.state.rag_engine
    history = [
        {"role": m.role, "content": m.content} for m in chat_request.history
    ]

    if chat_request.stream:

        async def event_generator():
            try:
                async for token in engine.chat_stream(
                    chat_request.query, chat_request.model, history
                ):
                    yield {"data": json.dumps({"token": token})}
                yield {"data": json.dumps({"done": True})}
            except Exception as exc:
                yield {"data": json.dumps({"error": str(exc)})}

        return EventSourceResponse(event_generator())

    try:
        result = await engine.chat(
            chat_request.query, chat_request.model, history
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return ChatResponse(
        response=result["content"],
        sources=result["sources"],
        model=chat_request.model,
    )
