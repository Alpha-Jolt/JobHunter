"""Text normalisation and similarity utilities."""

from __future__ import annotations

import re
import unicodedata


def normalise_for_comparison(text: str) -> str:
    """Normalise text for deterministic comparison operations.

    Operations: lowercase, unicode normalisation, remove punctuation,
    collapse whitespace.

    Args:
        text: Input text string.

    Returns:
        Normalised string suitable for set/token operations.
    """
    text = unicodedata.normalize("NFC", text).lower()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def token_overlap_ratio(a: str, b: str) -> float:
    """Compute the Jaccard token overlap ratio between two strings.

    Args:
        a: First string.
        b: Second string.

    Returns:
        Float 0.0–1.0 representing overlap ratio.
    """
    tokens_a = set(normalise_for_comparison(a).split())
    tokens_b = set(normalise_for_comparison(b).split())
    if not tokens_a or not tokens_b:
        return 0.0
    intersection = tokens_a & tokens_b
    union = tokens_a | tokens_b
    return len(intersection) / len(union)
