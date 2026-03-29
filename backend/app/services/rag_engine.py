import json
from collections.abc import AsyncGenerator

from app.core.prompt_store import prompt_store
from app.services.llm_client import LLMClient
from app.services.structured_store import StructuredStore
from app.services.vector_store import VectorStore

MAX_TOOL_ITERATIONS = 10


class RAGEngine:
    def __init__(
        self,
        llm_client: LLMClient,
        vector_store: VectorStore,
        structured_store: StructuredStore,
    ) -> None:
        self.llm = llm_client
        self.vector_store = vector_store
        self.structured_store = structured_store

    # -- Dynamic tool binding --------------------------------------------------

    def _get_tools(self) -> list[dict]:
        """Build tool definitions based on currently available data."""
        tools: list[dict] = []

        if self.vector_store.has_documents():
            tools.append({
                "type": "function",
                "function": {
                    "name": "vector_search",
                    "description": (
                        "Search through ingested unstructured documents "
                        "(markdown files, text) for relevant information. "
                        + self.vector_store.get_document_summary()
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": (
                                    "Natural language search query to find "
                                    "relevant document chunks"
                                ),
                            }
                        },
                        "required": ["query"],
                    },
                },
            })

        if self.structured_store.has_data():
            tools.append({
                "type": "function",
                "function": {
                    "name": "sql_query",
                    "description": (
                        "Query structured data (CSV files) using SQL. "
                        "Available data:\n"
                        + self.structured_store.get_schema_summary()
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": (
                                    "SQL query to execute against the structured "
                                    "data using DuckDB SQL syntax"
                                ),
                            }
                        },
                        "required": ["query"],
                    },
                },
            })

        return tools

    # -- Tool execution --------------------------------------------------------

    async def _execute_tool(
        self, name: str, arguments: dict
    ) -> tuple[str, set[str]]:
        """Execute a tool and return (result_text, source_names)."""
        if name == "vector_search":
            results = self.vector_store.search(arguments["query"])
            if not results:
                return "No relevant documents found.", set()

            sources = {r["metadata"].get("source", "unknown") for r in results}
            parts = []
            for r in results:
                source = r["metadata"].get("source", "unknown")
                section = r["metadata"].get("section", "")
                header = f"[{source}]" + (f" — {section}" if section else "")
                parts.append(f"{header}\n{r['text']}")
            return "\n\n---\n\n".join(parts), sources

        if name == "sql_query":
            result = self.structured_store.execute_query(arguments["query"])
            return result, {"structured_data"}

        return f"Unknown tool: {name}", set()

    # -- Message building ------------------------------------------------------

    def _build_messages(
        self, query: str, history: list[dict]
    ) -> list[dict]:
        system_content = prompt_store.get_prompt()
        tools = self._get_tools()

        if not tools:
            system_content += (
                "\n\nIMPORTANT: No documents have been ingested yet. "
                "You cannot look up any information. Inform the user that "
                "they need to upload documents first before you can answer "
                "questions about compliance, accounts, or scripts."
            )

        messages = [{"role": "system", "content": system_content}]
        for msg in history:
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": query})
        return messages

    # -- Non-streaming chat ----------------------------------------------------

    async def chat(
        self,
        query: str,
        model: str,
        history: list[dict] | None = None,
    ) -> dict:
        """Run the full tool-calling loop and return the final response."""
        messages = self._build_messages(query, history or [])
        tools = self._get_tools()
        sources: set[str] = set()

        for _ in range(MAX_TOOL_ITERATIONS):
            response = await self.llm.chat(
                messages, model, tools=tools or None
            )
            msg = response.choices[0].message

            if not msg.tool_calls:
                return {"content": msg.content or "", "sources": sorted(sources)}

            # Append assistant message with tool calls
            tool_calls_list = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in msg.tool_calls
            ]
            messages.append({
                "role": "assistant",
                "content": msg.content,
                "tool_calls": tool_calls_list,
            })

            for tc in msg.tool_calls:
                args = json.loads(tc.function.arguments)
                result, tool_sources = await self._execute_tool(
                    tc.function.name, args
                )
                sources.update(tool_sources)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result,
                })

        return {
            "content": (
                "I was unable to fully process your request after multiple "
                "attempts. Please try rephrasing."
            ),
            "sources": sorted(sources),
        }

    # -- Streaming chat --------------------------------------------------------

    async def chat_stream(
        self,
        query: str,
        model: str,
        history: list[dict] | None = None,
    ) -> AsyncGenerator[str, None]:
        """Stream the final answer. Tool-calling rounds are handled inline."""
        messages = self._build_messages(query, history or [])
        tools = self._get_tools()

        for _ in range(MAX_TOOL_ITERATIONS):
            stream = await self.llm.chat_stream(
                messages, model, tools=tools or None
            )

            collected_tool_calls: dict[int, dict] = {}
            has_tool_calls = False

            async for chunk in stream:
                if not chunk.choices:
                    continue
                delta = chunk.choices[0].delta

                if delta.tool_calls:
                    has_tool_calls = True
                    for tc_delta in delta.tool_calls:
                        idx = tc_delta.index
                        if idx not in collected_tool_calls:
                            collected_tool_calls[idx] = {
                                "id": "",
                                "name": "",
                                "arguments": "",
                            }
                        if tc_delta.id:
                            collected_tool_calls[idx]["id"] = tc_delta.id
                        if tc_delta.function:
                            if tc_delta.function.name:
                                collected_tool_calls[idx]["name"] = (
                                    tc_delta.function.name
                                )
                            if tc_delta.function.arguments:
                                collected_tool_calls[idx]["arguments"] += (
                                    tc_delta.function.arguments
                                )

                elif delta.content:
                    yield delta.content

            if not has_tool_calls:
                return  # Final answer was streamed above

            # Build assistant message with collected tool calls
            tool_calls_list = [
                {
                    "id": tc["id"],
                    "type": "function",
                    "function": {
                        "name": tc["name"],
                        "arguments": tc["arguments"],
                    },
                }
                for tc in collected_tool_calls.values()
            ]
            messages.append({
                "role": "assistant",
                "content": None,
                "tool_calls": tool_calls_list,
            })

            for tc_data in collected_tool_calls.values():
                args = json.loads(tc_data["arguments"])
                result, _ = await self._execute_tool(tc_data["name"], args)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc_data["id"],
                    "content": result,
                })

        yield (
            "I was unable to fully process your request. "
            "Please try rephrasing."
        )
