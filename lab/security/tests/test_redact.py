"""
Tests for PII redaction utilities.
"""

from lab.security.redact import PIIMatch, PIIRedactor


class TestPIIRedactor:
    """Test cases for PIIRedactor class."""

    def test_find_pii_ssn(self):
        """Test SSN detection."""
        redactor = PIIRedactor()

        test_cases = ["SSN: 123-45-6789", "SSN: 123 45 6789", "SSN: 123456789"]

        for text in test_cases:
            matches = redactor.find_pii(text)
            assert len(matches) >= 1
            assert any(match.pii_type == "ssn" for match in matches)

    def test_find_pii_email(self):
        """Test email detection."""
        redactor = PIIRedactor()

        text = "Contact me at test@example.com or admin@company.org"
        matches = redactor.find_pii(text)

        assert len(matches) == 2
        assert all(match.pii_type == "email" for match in matches)
        assert matches[0].original == "test@example.com"
        assert matches[1].original == "admin@company.org"

    def test_find_pii_credit_card(self):
        """Test credit card detection."""
        redactor = PIIRedactor()

        test_cases = [
            "Card: 1234-5678-9012-3456",
            "Card: 1234 5678 9012 3456",
            "Card: 1234567890123456",
        ]

        for text in test_cases:
            matches = redactor.find_pii(text)
            assert len(matches) >= 1
            assert any(match.pii_type == "credit_card" for match in matches)

    def test_find_pii_phone(self):
        """Test phone number detection."""
        redactor = PIIRedactor()

        test_cases = [
            "Call 555-123-4567",
            "Call (555) 123-4567",
            "Call 555.123.4567",
            "Call 5551234567",
            "Call 555 123 4567",
        ]

        for text in test_cases:
            matches = redactor.find_pii(text)
            assert len(matches) >= 1, f"No phone matches found in: {text}"
            assert any(
                match.pii_type == "phone" for match in matches
            ), f"No phone type found in matches for: {text}"

    def test_redact_text(self):
        """Test text redaction."""
        redactor = PIIRedactor()

        text = "Contact John at john@example.com, SSN: 123-45-6789, Card: 1234-5678-9012-3456"
        redacted, matches = redactor.redact_text(text)

        assert "[REDACTED-EMAIL]" in redacted
        assert "[REDACTED-SSN]" in redacted
        assert "[REDACTED-CREDIT_CARD]" in redacted
        assert "john@example.com" not in redacted
        assert "123-45-6789" not in redacted
        assert "1234-5678-9012-3456" not in redacted
        assert len(matches) == 3

    def test_redact_text_no_pii(self):
        """Test redaction with no PII."""
        redactor = PIIRedactor()

        text = "This is clean text with no PII"
        redacted, matches = redactor.redact_text(text)

        assert redacted == text
        assert len(matches) == 0

    def test_get_redaction_summary(self):
        """Test redaction summary generation."""
        redactor = PIIRedactor()

        matches = [
            PIIMatch("email", 0, 10, "test@test.com", "[REDACTED-EMAIL]"),
            PIIMatch("ssn", 20, 30, "123-45-6789", "[REDACTED-SSN]"),
            PIIMatch("email", 40, 50, "admin@test.com", "[REDACTED-EMAIL]"),
        ]

        summary = redactor.get_redaction_summary(matches)

        assert summary["email"] == 2
        assert summary["ssn"] == 1
        assert "phone" not in summary

    def test_pii_match_dataclass(self):
        """Test PIIMatch dataclass."""
        match = PIIMatch(
            pii_type="email",
            start=0,
            end=10,
            original="test@test.com",
            redacted="[REDACTED-EMAIL]",
        )

        assert match.pii_type == "email"
        assert match.start == 0
        assert match.end == 10
        assert match.original == "test@test.com"
        assert match.redacted == "[REDACTED-EMAIL]"
