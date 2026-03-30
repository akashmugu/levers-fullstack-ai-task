import shutil
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from app.core.prompt_store import PromptStore


@pytest.fixture()
def tmp_data_dir(monkeypatch: pytest.MonkeyPatch) -> Path:
    """Create a temporary data directory and patch settings to use it."""
    tmp = Path(tempfile.mkdtemp())
    monkeypatch.setattr("app.core.config.settings.data_dir", str(tmp))
    yield tmp
    shutil.rmtree(tmp, ignore_errors=True)


@pytest.fixture()
def prompt_store() -> PromptStore:
    return PromptStore()


@pytest.fixture()
def mock_rag_engine() -> AsyncMock:
    engine = AsyncMock()
    engine.chat.return_value = {
        "content": "Test response",
        "sources": ["test.md"],
    }

    async def fake_stream(query: str, model: str, history=None):
        for token in ["Hello", " ", "world"]:
            yield token

    engine.chat_stream = fake_stream
    return engine


@pytest.fixture()
def test_client(mock_rag_engine: AsyncMock) -> TestClient:
    """Create a test client with mocked services."""
    from app.main import app

    app.state.rag_engine = mock_rag_engine
    return TestClient(app)


@pytest.fixture()
def test_client_with_stores(
    tmp_data_dir: Path, mock_rag_engine: AsyncMock
) -> TestClient:
    """Test client with real vector/structured stores for document tests."""
    from app.main import app
    from app.services.structured_store import StructuredStore
    from app.services.vector_store import VectorStore

    app.state.rag_engine = mock_rag_engine
    app.state.vector_store = VectorStore()
    app.state.structured_store = StructuredStore()
    return TestClient(app)
