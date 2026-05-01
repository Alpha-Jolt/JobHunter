"""Text cleaner — normalises extracted resume text for LLM parsing."""

from __future__ import annotations

import re
import unicodedata


def clean_text(raw: str) -> str:
    """Normalise raw extracted text for LLM consumption.

    Operations:
    - Unicode normalisation (NFC)
    - Replace non-breaking spaces and other whitespace variants
    - Collapse multiple blank lines to a single blank line
    - Strip leading/trailing whitespace per line
    - Remove null bytes and control characters

    Args:
        raw: Raw text from extractor.

    Returns:
        Cleaned text string.
    """
    # Unicode normalisation
    text = unicodedata.normalize("NFC", raw)

    # Replace non-breaking spaces and other whitespace variants
    text = text.replace("\u00a0", " ").replace("\u200b", "").replace("\ufeff", "")

    # Remove control characters except newlines and tabs
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)

    # Strip each line
    lines = [line.strip() for line in text.splitlines()]

    # Collapse 3+ consecutive blank lines to 2
    cleaned_lines: list[str] = []
    blank_count = 0
    for line in lines:
        if not line:
            blank_count += 1
            if blank_count <= 2:
                cleaned_lines.append("")
        else:
            blank_count = 0
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines).strip()
