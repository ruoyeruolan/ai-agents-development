"""Split the roadmap into complete chapters."""

import re

from ._markdown import clean_markdown


def split_headings(text: str, source: str) -> list[dict]:
    """Keep each level-two heading and its following body in one chunk."""
    sections = re.split(r"\n(?=## )", clean_markdown(text))
    chunks = []

    for section in sections:
        section = section.strip()

        if not section:
            continue

        chunks.append(
            {
                "chunk_id": len(chunks),
                "source": source,
                "title": section.splitlines()[0].lstrip("#").strip(),
                "text": section,
            }
        )

    return chunks
