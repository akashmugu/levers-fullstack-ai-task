import re
import uuid


def chunk_markdown(
    text: str, source: str, max_chunk_size: int = 1000
) -> list[dict]:
    """Split markdown by headers, then by paragraphs if chunks are too large."""
    chunks: list[dict] = []
    sections = re.split(r"\n(?=## )", text)

    for section in sections:
        section = section.strip()
        if not section:
            continue

        if len(section) <= max_chunk_size:
            chunks.append(_make_chunk(section, source))
        else:
            _split_large_section(section, source, max_chunk_size, chunks)

    return chunks


def _split_large_section(
    section: str, source: str, max_size: int, chunks: list[dict]
) -> None:
    paragraphs = section.split("\n\n")
    current = ""
    for para in paragraphs:
        if len(current) + len(para) + 2 > max_size and current:
            chunks.append(_make_chunk(current.strip(), source))
            current = para
        else:
            current = f"{current}\n\n{para}" if current else para
    if current.strip():
        chunks.append(_make_chunk(current.strip(), source))


def _make_chunk(text: str, source: str) -> dict:
    title_match = re.match(r"^#{1,3}\s+(.+)", text)
    title = title_match.group(1) if title_match else ""
    return {
        "id": str(uuid.uuid4()),
        "text": text,
        "metadata": {"source": source, "section": title},
    }
