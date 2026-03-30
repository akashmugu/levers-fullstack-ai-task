from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services.rag_engine import MAX_TOOL_ITERATIONS, RAGEngine


@pytest.fixture()
def llm_client() -> AsyncMock:
    return AsyncMock()


@pytest.fixture()
def vector_store() -> MagicMock:
    store = MagicMock()
    store.has_documents.return_value = False
    store.search.return_value = []
    store.get_document_summary.return_value = "Available documents: test.md"
    return store


@pytest.fixture()
def structured_store() -> MagicMock:
    store = MagicMock()
    store.has_data.return_value = False
    store.tables = {}
    store.get_schema_summary.return_value = ""
    return store


@pytest.fixture()
def engine(
    llm_client: AsyncMock,
    vector_store: MagicMock,
    structured_store: MagicMock,
) -> RAGEngine:
    return RAGEngine(llm_client, vector_store, structured_store)


class TestGetTools:
    def test_empty_stores_returns_no_tools(self, engine: RAGEngine) -> None:
        assert engine._get_tools() == []

    def test_vector_store_only(
        self, engine: RAGEngine, vector_store: MagicMock
    ) -> None:
        vector_store.has_documents.return_value = True
        tools = engine._get_tools()
        assert len(tools) == 1
        assert tools[0]["function"]["name"] == "vector_search"

    def test_structured_store_only(
        self, engine: RAGEngine, structured_store: MagicMock
    ) -> None:
        structured_store.has_data.return_value = True
        tools = engine._get_tools()
        assert len(tools) == 1
        assert tools[0]["function"]["name"] == "sql_query"

    def test_both_stores(
        self,
        engine: RAGEngine,
        vector_store: MagicMock,
        structured_store: MagicMock,
    ) -> None:
        vector_store.has_documents.return_value = True
        structured_store.has_data.return_value = True
        tools = engine._get_tools()
        names = {t["function"]["name"] for t in tools}
        assert names == {"vector_search", "sql_query"}


class TestBuildMessages:
    def test_injects_system_prompt(self, engine: RAGEngine) -> None:
        messages = engine._build_messages("hello", [])
        assert messages[0]["role"] == "system"
        assert len(messages[0]["content"]) > 0

    def test_appends_no_documents_warning_when_empty(self, engine: RAGEngine) -> None:
        messages = engine._build_messages("hello", [])
        assert "No documents have been ingested" in messages[0]["content"]

    def test_no_warning_when_documents_exist(
        self, engine: RAGEngine, vector_store: MagicMock
    ) -> None:
        vector_store.has_documents.return_value = True
        messages = engine._build_messages("hello", [])
        assert "No documents have been ingested" not in messages[0]["content"]

    def test_includes_history(self, engine: RAGEngine) -> None:
        history = [
            {"role": "user", "content": "first"},
            {"role": "assistant", "content": "reply"},
        ]
        messages = engine._build_messages("follow-up", history)
        assert messages[1] == {"role": "user", "content": "first"}
        assert messages[2] == {"role": "assistant", "content": "reply"}
        assert messages[3] == {"role": "user", "content": "follow-up"}

    def test_user_query_is_last(self, engine: RAGEngine) -> None:
        messages = engine._build_messages("my question", [])
        assert messages[-1] == {"role": "user", "content": "my question"}


class TestExecuteTool:
    async def test_vector_search_returns_results(
        self, engine: RAGEngine, vector_store: MagicMock
    ) -> None:
        vector_store.search.return_value = [
            {
                "text": "Call hours are 8 AM to 9 PM",
                "metadata": {"source": "fdcpa.md", "section": "Hours"},
            }
        ]
        result, sources = await engine._execute_tool(
            "vector_search", {"query": "calling hours"}
        )
        assert "8 AM to 9 PM" in result
        assert sources == {"fdcpa.md"}

    async def test_vector_search_no_results(
        self, engine: RAGEngine, vector_store: MagicMock
    ) -> None:
        vector_store.search.return_value = []
        result, sources = await engine._execute_tool(
            "vector_search", {"query": "irrelevant"}
        )
        assert "No relevant documents found" in result
        assert sources == set()

    async def test_sql_query(
        self, engine: RAGEngine, structured_store: MagicMock
    ) -> None:
        structured_store.execute_query.return_value = (
            "account_id | name\n--- | ---\nACC-001 | John"
        )
        structured_store.tables = {"accounts.csv": {}}
        result, sources = await engine._execute_tool(
            "sql_query", {"query": "SELECT * FROM accounts.csv"}
        )
        assert "John" in result
        assert "accounts.csv" in sources

    async def test_unknown_tool(self, engine: RAGEngine) -> None:
        result, sources = await engine._execute_tool("bogus", {})
        assert "Unknown tool" in result
        assert sources == set()


class TestChat:
    async def test_simple_response_no_tools(
        self, engine: RAGEngine, llm_client: AsyncMock
    ) -> None:
        """LLM responds directly without calling any tools."""
        mock_msg = MagicMock()
        mock_msg.tool_calls = None
        mock_msg.content = "I cannot help without documents."

        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=mock_msg)]
        llm_client.chat.return_value = mock_response

        result = await engine.chat("hello", "test-model")
        assert result["content"] == "I cannot help without documents."
        assert result["sources"] == []

    async def test_tool_call_then_response(
        self,
        engine: RAGEngine,
        llm_client: AsyncMock,
        vector_store: MagicMock,
    ) -> None:
        """LLM makes a tool call, gets results, then responds."""
        vector_store.has_documents.return_value = True
        vector_store.search.return_value = [
            {
                "text": "Call between 8 AM and 9 PM",
                "metadata": {"source": "fdcpa.md", "section": "Hours"},
            }
        ]

        # First call: LLM requests tool
        tool_call = MagicMock()
        tool_call.id = "call_1"
        tool_call.function.name = "vector_search"
        tool_call.function.arguments = '{"query": "calling hours"}'

        msg_with_tool = MagicMock()
        msg_with_tool.tool_calls = [tool_call]
        msg_with_tool.content = None

        # Second call: LLM responds with final answer
        msg_final = MagicMock()
        msg_final.tool_calls = None
        msg_final.content = "You can call between 8 AM and 9 PM."

        llm_client.chat.side_effect = [
            MagicMock(choices=[MagicMock(message=msg_with_tool)]),
            MagicMock(choices=[MagicMock(message=msg_final)]),
        ]

        result = await engine.chat("When can I call?", "test-model")
        assert result["content"] == "You can call between 8 AM and 9 PM."
        assert "fdcpa.md" in result["sources"]
        assert llm_client.chat.call_count == 2

    async def test_max_iterations_returns_fallback(
        self, engine: RAGEngine, llm_client: AsyncMock, vector_store: MagicMock
    ) -> None:
        """If LLM keeps requesting tools beyond the limit, return fallback."""
        vector_store.has_documents.return_value = True
        vector_store.search.return_value = []

        tool_call = MagicMock()
        tool_call.id = "call_loop"
        tool_call.function.name = "vector_search"
        tool_call.function.arguments = '{"query": "loop"}'

        msg = MagicMock()
        msg.tool_calls = [tool_call]
        msg.content = None

        llm_client.chat.return_value = MagicMock(choices=[MagicMock(message=msg)])

        result = await engine.chat("loop query", "test-model")
        assert "unable to fully process" in result["content"].lower()
        assert llm_client.chat.call_count == MAX_TOOL_ITERATIONS


class TestChatStream:
    async def test_stream_direct_response(
        self, engine: RAGEngine, llm_client: AsyncMock
    ) -> None:
        """Streaming without tool calls yields tokens directly."""

        async def fake_stream():
            for text in ["Hello", " ", "world"]:
                chunk = MagicMock()
                chunk.choices = [MagicMock()]
                chunk.choices[0].delta.tool_calls = None
                chunk.choices[0].delta.content = text
                yield chunk

        llm_client.chat_stream.return_value = fake_stream()

        tokens = []
        async for token in engine.chat_stream("hi", "test-model"):
            tokens.append(token)

        assert "".join(tokens) == "Hello world"
