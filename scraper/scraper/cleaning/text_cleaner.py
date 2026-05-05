"""Text normalization utilities."""

import html
import re
import unicodedata
from typing import List, Optional

_CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_HTML_TAG_RE = re.compile(r"<[^>]+>")
_WHITESPACE_RE = re.compile(r"\s+")
_EXCESS_DASH_RE = re.compile(r"-{3,}")
_EXCESS_UNDERSCORE_RE = re.compile(r"_{3,}")


class TextCleaner:
    """Stateless text cleaning utilities."""

    @staticmethod
    def clean_text(text: Optional[str]) -> Optional[str]:
        """
        Full cleaning pipeline:
        1. Unicode NFKD normalisation
        2. Remove control characters
        3. Decode HTML entities
        4. Strip HTML tags
        5. Collapse whitespace
        6. Trim excess punctuation
        """
        if text is None:
            return None
        text = unicodedata.normalize("NFKD", text)
        text = _CONTROL_RE.sub("", text)
        text = html.unescape(text)
        text = _HTML_TAG_RE.sub(" ", text)
        text = _WHITESPACE_RE.sub(" ", text)
        text = _EXCESS_DASH_RE.sub("--", text)
        text = _EXCESS_UNDERSCORE_RE.sub("__", text)
        return text.strip() or None

    @staticmethod
    def clean_field(text: str) -> str:
        """Clean a single required field; returns empty string on failure."""
        result = TextCleaner.clean_text(text)
        return result or ""

    @staticmethod
    def clean_list(items: List[str]) -> List[str]:
        """Clean each item and deduplicate while preserving order."""
        seen = set()
        result = []
        for item in items:
            cleaned = TextCleaner.clean_field(item)
            if cleaned and cleaned not in seen:
                seen.add(cleaned)
                result.append(cleaned)
        return result

    @staticmethod
    def remove_html_tags(html_text: str) -> str:
        return _HTML_TAG_RE.sub(" ", html_text).strip()

    @staticmethod
    def decode_html_entities(text: str) -> str:
        return html.unescape(text)
