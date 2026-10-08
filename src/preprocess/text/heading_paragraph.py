"""Split chapter bodies into paragraphs while retaining their headings."""

import re

from .heading import split_headings


def split_heading_paragraphs(text: str, source: str) -> list[dict]:
    """Prefix each paragraph with its heading and keep labels with the body."""
    sections = split_headings(text, source)
    chunks = []

    for section in sections:
        heading, _, section_body = section["text"].partition("\n")
        pending_label = ""

        for paragraph in re.split(r"\n\s*\n", section_body.strip()):
            paragraph = paragraph.strip()

            if not paragraph:
                continue

            # Keep standalone labels such as **Learn:** with the next paragraph.
            if re.fullmatch(r"\*\*[^*\n]+:\*\*", paragraph):
                pending_label = paragraph
                continue

            if pending_label:
                paragraph = f"{pending_label}\n{paragraph}"
                pending_label = ""

            chunks.append(
                {
                    "chunk_id": len(chunks),
                    "source": source,
                    "title": section["title"],
                    "body": paragraph,
                    "text": f"{heading}\n\n{paragraph}",
                }
            )

    return chunks
