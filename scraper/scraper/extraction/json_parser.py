"""JSON extraction utilities with dot-notation key paths."""

from typing import Any, Dict, List

from scraper.logging_.logger import Logger

_logger = Logger.get_logger(__name__)


class JSONExtractor:
    """Extract values from nested JSON using dot-notation paths."""

    @staticmethod
    def extract_from_json(data: Dict[str, Any], key_path: str) -> Any:
        """
        Traverse nested dict using dot-notation path.

        Example: extract_from_json(data, "job.salary.text")
        """
        parts = key_path.split(".")
        current = data
        for part in parts:
            if not isinstance(current, dict):
                return None
            current = current.get(part)
            if current is None:
                return None
        return current

    @staticmethod
    def extract_array_values(data: Dict[str, Any], key: str) -> List[Any]:
        """Return list at top-level key, or empty list."""
        value = data.get(key)
        if isinstance(value, list):
            return value
        return []

    @staticmethod
    def safe_extract(
        data: Dict[str, Any],
        key_path: str,
        default: Any = None,
    ) -> Any:
        """extract_from_json with a fallback default."""
        try:
            result = JSONExtractor.extract_from_json(data, key_path)
            return result if result is not None else default
        except Exception as exc:
            _logger.warning(
                "safe_extract failed",
                extra_data={"key_path": key_path, "error": str(exc)},
            )
            return default
