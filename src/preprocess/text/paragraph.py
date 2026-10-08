"""The original blank-line splitting exercise."""


def split_paragraphs(text: str, source: str) -> list[dict]:
    """Return paragraph chunks without adding their chapter headings."""
    chunks = []

    for paragraph in text.split("\n\n"):
        paragraph = paragraph.strip()

        if not paragraph or paragraph == "---":
            continue

        if paragraph.startswith("<!--") and paragraph.endswith("-->"):
            continue

        chunks.append(
            {
                "chunk_id": len(chunks),
                "source": source,
                "text": paragraph,
            }
        )

    return chunks
