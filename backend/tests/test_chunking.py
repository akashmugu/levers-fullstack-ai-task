from app.utils.chunking import chunk_markdown


class TestChunkMarkdown:
    def test_single_small_section(self) -> None:
        text = "## Section One\nSome content here."
        chunks = chunk_markdown(text, source="test.md")
        assert len(chunks) == 1
        assert chunks[0]["text"] == text
        assert chunks[0]["metadata"]["source"] == "test.md"
        assert chunks[0]["metadata"]["section"] == "Section One"

    def test_multiple_sections(self) -> None:
        text = "## First\nContent A\n\n## Second\nContent B"
        chunks = chunk_markdown(text, source="doc.md")
        assert len(chunks) == 2
        assert "Content A" in chunks[0]["text"]
        assert "Content B" in chunks[1]["text"]

    def test_large_section_is_split(self) -> None:
        paragraphs = [f"Paragraph {i}. " + "x" * 80 for i in range(15)]
        text = "## Big Section\n\n" + "\n\n".join(paragraphs)
        chunks = chunk_markdown(text, source="big.md", max_chunk_size=200)
        assert len(chunks) > 1
        for chunk in chunks:
            assert chunk["metadata"]["source"] == "big.md"

    def test_empty_text(self) -> None:
        chunks = chunk_markdown("", source="empty.md")
        assert chunks == []

    def test_unique_ids(self) -> None:
        text = "## A\nContent\n\n## B\nContent"
        chunks = chunk_markdown(text, source="test.md")
        ids = [c["id"] for c in chunks]
        assert len(ids) == len(set(ids))

    def test_no_header_section(self) -> None:
        text = "Just some plain text without any headers."
        chunks = chunk_markdown(text, source="plain.md")
        assert len(chunks) == 1
        assert chunks[0]["metadata"]["section"] == ""
