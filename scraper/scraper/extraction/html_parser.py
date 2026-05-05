"""HTML parsing utilities using BeautifulSoup."""

from typing import Dict, List, Optional

from bs4 import BeautifulSoup

from scraper.logging_.logger import Logger

_logger = Logger.get_logger(__name__)


class HTMLExtractor:
    """Extract data from HTML strings using CSS selectors."""

    @staticmethod
    def extract_by_selector(
        html: str,
        selector: str,
        attr: Optional[str] = None,
    ) -> Optional[str]:
        """Return text (or attribute value) of the first matching element."""
        try:
            soup = BeautifulSoup(html, "lxml")
            el = soup.select_one(selector)
            if el is None:
                return None
            return el.get(attr) if attr else el.get_text(strip=True) or None
        except Exception as exc:
            _logger.warning(
                "extract_by_selector failed",
                extra_data={"selector": selector, "error": str(exc)},
            )
            return None

    @staticmethod
    def extract_all_by_selector(html: str, selector: str) -> List[str]:
        """Return text of all matching elements."""
        try:
            soup = BeautifulSoup(html, "lxml")
            return [
                el.get_text(strip=True) for el in soup.select(selector) if el.get_text(strip=True)
            ]
        except Exception as exc:
            _logger.warning(
                "extract_all_by_selector failed",
                extra_data={"selector": selector, "error": str(exc)},
            )
            return []

    @staticmethod
    def extract_by_xpath(html: str, xpath: str) -> Optional[str]:
        """Return text of first XPath match (requires lxml)."""
        try:
            from lxml import etree  # noqa: PLC0415

            tree = etree.fromstring(html.encode(), etree.HTMLParser())
            results = tree.xpath(xpath)
            if not results:
                return None
            node = results[0]
            text = (
                node.text_content().strip() if hasattr(node, "text_content") else str(node).strip()
            )
            return text or None
        except Exception as exc:
            _logger.warning(
                "extract_by_xpath failed",
                extra_data={"xpath": xpath, "error": str(exc)},
            )
            return None

    @staticmethod
    def extract_table_data(html: str, table_selector: str) -> List[Dict[str, str]]:
        """Extract rows from an HTML table as list of dicts."""
        try:
            soup = BeautifulSoup(html, "lxml")
            table = soup.select_one(table_selector)
            if not table:
                return []
            headers = [th.get_text(strip=True) for th in table.select("th")]
            rows = []
            for tr in table.select("tr"):
                cells = [td.get_text(strip=True) for td in tr.select("td")]
                if cells and headers:
                    rows.append(dict(zip(headers, cells)))
            return rows
        except Exception as exc:
            _logger.warning(
                "extract_table_data failed",
                extra_data={"error": str(exc)},
            )
            return []
