import json
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient


class TestHealthEndpoint:
    def test_health_returns_ok(self, test_client: TestClient) -> None:
        response = test_client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestChatEndpoint:
    def test_non_streaming_chat(
        self, test_client: TestClient, mock_rag_engine: AsyncMock
    ) -> None:
        response = test_client.post(
            "/api/chat",
            json={"query": "What is FDCPA?", "model": "test-model"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["response"] == "Test response"
        assert data["sources"] == ["test.md"]
        assert data["model"] == "test-model"

    def test_streaming_chat(self, test_client: TestClient) -> None:
        response = test_client.post(
            "/api/chat",
            json={
                "query": "Hello",
                "model": "test-model",
                "stream": True,
            },
        )
        assert response.status_code == 200

        events = []
        for line in response.iter_lines():
            if line.startswith("data:"):
                events.append(json.loads(line[len("data:") :].strip()))

        tokens = [e["token"] for e in events if "token" in e]
        assert "".join(tokens) == "Hello world"
        assert any(e.get("done") for e in events)

    def test_chat_with_history(
        self, test_client: TestClient, mock_rag_engine: AsyncMock
    ) -> None:
        response = test_client.post(
            "/api/chat",
            json={
                "query": "Follow-up question",
                "model": "test-model",
                "history": [
                    {"role": "user", "content": "First question"},
                    {"role": "assistant", "content": "First answer"},
                ],
            },
        )
        assert response.status_code == 200

    def test_chat_llm_error_returns_502(
        self, test_client: TestClient, mock_rag_engine: AsyncMock
    ) -> None:
        mock_rag_engine.chat.side_effect = RuntimeError("LLM unavailable")
        response = test_client.post(
            "/api/chat",
            json={"query": "test", "model": "test-model"},
        )
        assert response.status_code == 502


class TestConfigEndpoints:
    def test_get_system_prompt(self, test_client: TestClient) -> None:
        response = test_client.get("/api/config/system-prompt")
        assert response.status_code == 200
        assert "prompt" in response.json()
        assert len(response.json()["prompt"]) > 0

    def test_update_system_prompt(self, test_client: TestClient) -> None:
        new_prompt = "You are a test assistant."
        response = test_client.put(
            "/api/config/system-prompt",
            json={"prompt": new_prompt},
        )
        assert response.status_code == 200
        assert response.json()["prompt"] == new_prompt

    def test_get_models(self, test_client: TestClient) -> None:
        response = test_client.get("/api/config/models")
        assert response.status_code == 200
        data = response.json()
        assert "models" in data
        assert "default" in data
        assert len(data["models"]) == 2
        types = {m["type"] for m in data["models"]}
        assert types == {"thinking", "standard"}


class TestDocumentsEndpoint:
    def test_upload_unsupported_file_type(self, test_client: TestClient) -> None:
        response = test_client.post(
            "/api/documents",
            files={"file": ("bad.exe", b"content", "application/octet-stream")},
        )
        assert response.status_code == 400
        assert "Unsupported file type" in response.json()["detail"]

    def test_delete_nonexistent_document(self, test_client: TestClient) -> None:
        response = test_client.delete("/api/documents/nonexistent.md")
        assert response.status_code == 404

    def test_upload_markdown(self, test_client_with_stores: TestClient) -> None:
        md_content = b"## Test Section\nSome compliance content here."
        response = test_client_with_stores.post(
            "/api/documents",
            files={"file": ("test.md", md_content, "text/markdown")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["filename"] == "test.md"
        assert data["doc_type"] == "unstructured"
        assert "chunks" in data["detail"]

    def test_upload_csv(self, test_client_with_stores: TestClient) -> None:
        csv_content = b"account_id,name,status\nACC-001,John,active\n"
        response = test_client_with_stores.post(
            "/api/documents",
            files={"file": ("accounts.csv", csv_content, "text/csv")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["filename"] == "accounts.csv"
        assert data["doc_type"] == "structured"

    def test_list_documents(self, test_client_with_stores: TestClient) -> None:
        # Upload a markdown file first
        test_client_with_stores.post(
            "/api/documents",
            files={"file": ("doc.md", b"## Title\nContent", "text/markdown")},
        )
        response = test_client_with_stores.get("/api/documents")
        assert response.status_code == 200
        data = response.json()
        assert "unstructured" in data
        assert "structured" in data
        assert "doc.md" in data["unstructured"]
