from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import chat, config, documents
from app.services.llm_client import LLMClient
from app.services.rag_engine import RAGEngine
from app.services.structured_store import StructuredStore
from app.services.vector_store import VectorStore

app = FastAPI(title="Debt Collection Agent Assistant", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

llm_client = LLMClient()
vector_store = VectorStore()
structured_store = StructuredStore()
rag_engine = RAGEngine(llm_client, vector_store, structured_store)

app.state.rag_engine = rag_engine
app.state.vector_store = vector_store
app.state.structured_store = structured_store

app.include_router(chat.router)
app.include_router(documents.router)
app.include_router(config.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
