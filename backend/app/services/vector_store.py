from pathlib import Path

import chromadb

from app.core.config import settings


class VectorStore:
    def __init__(self) -> None:
        persist_dir = Path(settings.data_dir) / "chroma"
        persist_dir.mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=str(persist_dir))
        self.collection = self.client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"},
        )

    def add_chunks(self, chunks: list[dict]) -> None:
        if not chunks:
            return
        self.collection.add(
            ids=[c["id"] for c in chunks],
            documents=[c["text"] for c in chunks],
            metadatas=[c["metadata"] for c in chunks],
        )

    def search(self, query: str, n_results: int = 5) -> list[dict]:
        if self.collection.count() == 0:
            return []
        actual_n = min(n_results, self.collection.count())
        results = self.collection.query(query_texts=[query], n_results=actual_n)

        output = []
        for i in range(len(results["ids"][0])):
            output.append({
                "id": results["ids"][0][i],
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i] if results.get("distances") else None,
            })
        return output

    def has_documents(self) -> bool:
        return self.collection.count() > 0

    def get_document_summary(self) -> str:
        if not self.has_documents():
            return "No documents ingested."
        all_meta = self.collection.get()["metadatas"]
        sources = sorted({m.get("source", "unknown") for m in all_meta})
        return f"Available documents: {', '.join(sources)}"

    def document_exists(self, source: str) -> bool:
        results = self.collection.get(where={"source": source})
        return len(results["ids"]) > 0

    def delete_document(self, source: str) -> None:
        results = self.collection.get(where={"source": source})
        if results["ids"]:
            self.collection.delete(ids=results["ids"])
