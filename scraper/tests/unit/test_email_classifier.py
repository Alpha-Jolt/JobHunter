"""Unit tests for email_classifier — classification, trust levels, extraction."""

import pytest

from scraper.sources.company_discovery.enrichment.email_classifier import (
    classify_email,
    extract_emails_from_text,
    is_valid_email,
)


class TestIsValidEmail:
    def test_valid_corporate_email(self):
        assert is_valid_email("hr@acme.com") is True

    def test_valid_gmail(self):
        assert is_valid_email("user@gmail.com") is True

    def test_invalid_no_at(self):
        assert is_valid_email("noatsign.com") is False

    def test_invalid_no_domain(self):
        assert is_valid_email("user@") is False

    def test_invalid_no_tld(self):
        assert is_valid_email("user@domain") is False

    def test_empty_string(self):
        assert is_valid_email("") is False


class TestClassifyEmail:
    # --- HR / Career classification ---

    def test_careers_local_part(self):
        category, trust = classify_email("careers@acme.com")
        assert category == "career"

    def test_hr_local_part(self):
        category, trust = classify_email("hr@company.co.in")
        assert category == "career"

    def test_jobs_local_part(self):
        category, trust = classify_email("jobs@startup.io")
        assert category == "career"

    def test_recruitment_local_part(self):
        category, trust = classify_email("recruitment@bigcorp.com")
        assert category == "career"

    def test_talent_local_part(self):
        category, trust = classify_email("talent@example.com")
        assert category == "career"

    def test_hiring_local_part(self):
        category, trust = classify_email("hiring@techfirm.in")
        assert category == "career"

    def test_apply_local_part(self):
        category, trust = classify_email("apply@company.com")
        assert category == "career"

    # --- General classification ---

    def test_info_is_general(self):
        category, trust = classify_email("info@acme.com")
        assert category == "general"

    def test_sales_is_general(self):
        category, trust = classify_email("sales@acme.com")
        assert category == "general"

    def test_support_is_general(self):
        category, trust = classify_email("support@startup.io")
        assert category == "general"

    # --- Trust levels ---

    def test_corporate_email_is_unverified(self):
        _, trust = classify_email("hr@acme.com")
        assert trust == "unverified"

    def test_gmail_is_low_trust(self):
        _, trust = classify_email("careers@gmail.com")
        assert trust == "low_trust"

    def test_yahoo_is_low_trust(self):
        _, trust = classify_email("hr@yahoo.com")
        assert trust == "low_trust"

    def test_rediffmail_is_low_trust(self):
        _, trust = classify_email("jobs@rediffmail.com")
        assert trust == "low_trust"

    def test_outlook_is_low_trust(self):
        _, trust = classify_email("careers@outlook.com")
        assert trust == "low_trust"

    # --- Invalid emails return None ---

    def test_invalid_email_returns_none(self):
        assert classify_email("not-an-email") is None

    def test_empty_string_returns_none(self):
        assert classify_email("") is None


class TestExtractEmailsFromText:
    def test_extracts_single_email(self):
        text = "Contact us at hr@acme.com for more info."
        emails = extract_emails_from_text(text)
        assert "hr@acme.com" in emails

    def test_extracts_multiple_emails(self):
        text = "Email hr@acme.com or careers@acme.com"
        emails = extract_emails_from_text(text)
        assert len(emails) == 2

    def test_deduplicates_emails(self):
        text = "hr@acme.com and hr@acme.com again"
        emails = extract_emails_from_text(text)
        assert emails.count("hr@acme.com") == 1

    def test_discards_invalid_format(self):
        text = "Not an email: @domain.com or user@"
        emails = extract_emails_from_text(text)
        assert emails == []

    def test_returns_lowercase(self):
        text = "Contact HR@ACME.COM"
        emails = extract_emails_from_text(text)
        assert "hr@acme.com" in emails

    def test_empty_text(self):
        assert extract_emails_from_text("") == []
