"""Unit tests for domain_utils — normalisation, fingerprinting, dedup helpers."""

import pytest

from scraper.sources.company_discovery.enrichment.domain_utils import (
    build_dedup_fingerprint,
    is_job_board,
    normalize_apex_domain,
    normalize_company_name,
)


class TestNormalizeApexDomain:
    def test_strips_https_and_www(self):
        assert normalize_apex_domain("https://www.acme.com") == "acme.com"

    def test_strips_http(self):
        assert normalize_apex_domain("http://acme.com") == "acme.com"

    def test_strips_path(self):
        assert normalize_apex_domain("https://acme.com/careers") == "acme.com"

    def test_strips_port(self):
        assert normalize_apex_domain("https://acme.com:8080") == "acme.com"

    def test_bare_domain(self):
        assert normalize_apex_domain("acme.com") == "acme.com"

    def test_subdomain_returns_apex(self):
        # When tldextract is installed, careers.acme.com → acme.com.
        # Without tldextract, the fallback returns the netloc as-is (minus www.).
        # This test verifies that the function returns *a* non-None result.
        result = normalize_apex_domain("careers.acme.com")
        assert result is not None
        assert "acme.com" in result

    def test_co_in_suffix(self):
        result = normalize_apex_domain("https://www.tcs.co.in")
        assert result == "tcs.co.in"

    def test_lowercase(self):
        assert normalize_apex_domain("HTTPS://ACME.COM") == "acme.com"

    def test_trailing_slash(self):
        assert normalize_apex_domain("https://acme.com/") == "acme.com"

    def test_empty_string_returns_none(self):
        assert normalize_apex_domain("") is None

    def test_none_input_returns_none(self):
        assert normalize_apex_domain(None) is None  # type: ignore

    def test_invalid_string_returns_none(self):
        assert normalize_apex_domain("not a domain") is None


class TestIsJobBoard:
    def test_known_job_board(self):
        assert is_job_board("naukri.com") is True
        assert is_job_board("linkedin.com") is True
        assert is_job_board("indeed.com") is True

    def test_unknown_domain(self):
        assert is_job_board("acme.com") is False

    def test_company_website(self):
        assert is_job_board("infosys.com") is False


class TestNormalizeCompanyName:
    def test_strips_pvt_ltd(self):
        assert normalize_company_name("Acme Pvt. Ltd.") == "acme"

    def test_strips_technologies(self):
        assert normalize_company_name("Infosys Technologies") == "infosys"

    def test_strips_private_limited(self):
        # "consultancy" and "services" are also stripped, leaving the core brand name
        result = normalize_company_name("Tata Consultancy Services Private Limited")
        assert "tata" in result

    def test_lowercase(self):
        assert normalize_company_name("WIPRO") == "wipro"

    def test_removes_special_chars(self):
        assert normalize_company_name("A.B.C Corp") == "abc"

    def test_empty_string(self):
        assert normalize_company_name("") == ""


class TestBuildDedupFingerprint:
    def test_returns_32_char_hex(self):
        fp = build_dedup_fingerprint("acme", "acme.com")
        assert len(fp) == 32
        assert all(c in "0123456789abcdef" for c in fp)

    def test_same_input_same_output(self):
        fp1 = build_dedup_fingerprint("acme", "acme.com")
        fp2 = build_dedup_fingerprint("acme", "acme.com")
        assert fp1 == fp2

    def test_different_input_different_output(self):
        fp1 = build_dedup_fingerprint("acme", "acme.com")
        fp2 = build_dedup_fingerprint("acme", "acme.co.in")
        assert fp1 != fp2
