"""
Tests for Guardian security module.
"""

import os
from unittest.mock import patch
from lab.security.guardian import Guardian


class TestGuardian:
    """Test cases for Guardian class."""

    def test_default_allowlist(self):
        """Test default allowlist when no environment variable is set."""
        with patch.dict(os.environ, {}, clear=True):
            guardian = Guardian()
            assert "health" in guardian.allowlist
            assert "tools/summarize" in guardian.allowlist
            assert "tools/search_docs" not in guardian.allowlist

    def test_custom_allowlist(self):
        """Test custom allowlist from environment variable."""
        with patch.dict(
            os.environ, {"GUARDIAN_ALLOW_TOOLS": "health,tools/summarize,tools/custom"}
        ):
            guardian = Guardian()
            assert "health" in guardian.allowlist
            assert "tools/summarize" in guardian.allowlist
            assert "tools/custom" in guardian.allowlist
            assert "tools/search_docs" not in guardian.allowlist

    def test_is_tool_allowed(self):
        """Test tool allowlist checking."""
        with patch.dict(os.environ, {"GUARDIAN_ALLOW_TOOLS": "health,tools/summarize"}):
            guardian = Guardian()
            assert guardian.is_tool_allowed("health") is True
            assert guardian.is_tool_allowed("tools/summarize") is True
            assert guardian.is_tool_allowed("tools/search_docs") is False
            assert guardian.is_tool_allowed("unauthorized_tool") is False

    def test_guard_tool_decorator_allowed(self):
        """Test guard decorator with allowed tool."""
        with patch.dict(os.environ, {"GUARDIAN_ALLOW_TOOLS": "test_tool"}):
            guardian = Guardian()

            @guardian.guard_tool("test_tool")
            def test_function():
                return {"result": "success"}

            result = test_function()
            assert result == {"result": "success"}

    def test_guard_tool_decorator_blocked(self):
        """Test guard decorator with blocked tool."""
        with patch.dict(os.environ, {"GUARDIAN_ALLOW_TOOLS": "allowed_tool"}):
            guardian = Guardian()

            @guardian.guard_tool("blocked_tool")
            def test_function():
                return {"result": "success"}

            result = test_function()
            assert "error" in result
            assert result["error"] == "Unauthorized"

    def test_redact_output_enabled(self):
        """Test PII redaction when enabled."""
        with patch.dict(os.environ, {"GUARDIAN_REDACT_OUTPUTS": "true"}):
            guardian = Guardian()

            test_data = {
                "email": "test@example.com",
                "ssn": "123-45-6789",
                "clean_data": "no pii here",
            }

            result = guardian._redact_output(test_data)
            assert result["email"] == "[REDACTED-EMAIL]"
            assert result["ssn"] == "[REDACTED-SSN]"
            assert result["clean_data"] == "no pii here"

    def test_redact_output_disabled(self):
        """Test PII redaction when disabled."""
        with patch.dict(os.environ, {"GUARDIAN_REDACT_OUTPUTS": "false"}):
            guardian = Guardian()

            test_data = {"email": "test@example.com", "ssn": "123-45-6789"}

            result = guardian._redact_output(test_data)
            # When redaction is disabled, data should pass through unchanged
            assert result["email"] == "test@example.com"
            assert result["ssn"] == "123-45-6789"

    def test_redact_string_patterns(self):
        """Test PII redaction patterns."""
        guardian = Guardian()

        test_cases = [
            ("My SSN is 123-45-6789", "My SSN is [REDACTED-SSN]"),
            ("Email me at test@example.com", "Email me at [REDACTED-EMAIL]"),
            ("Call 555-123-4567", "Call [REDACTED-PHONE]"),
            ("Card: 1234-5678-9012-3456", "Card: [REDACTED-CC]"),
            ("No PII here", "No PII here"),
        ]

        for input_text, expected in test_cases:
            result = guardian._redact_string(input_text)
            assert result == expected
