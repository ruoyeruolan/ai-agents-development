"""Shared cleanup for the roadmap's heading-based splitting strategies."""


def clean_markdown(text: str) -> str:
    """Remove horizontal rules and standalone single-line HTML comments."""
    lines = []

    for line in text.splitlines():
        stripped = line.strip()

        if stripped == "---":
            continue

        if stripped.startswith("<!--") and stripped.endswith("-->"):
            continue

        # Preserve the indentation of the original Markdown line.
        lines.append(line)

    return "\n".join(lines)
