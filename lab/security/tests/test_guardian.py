import os
from lab.security.guardian import Guardian

def test_guardian_allowlist():
    os.environ["GUARDIAN_ALLOW_TOOLS"] = "foo,bar"
    g = Guardian()
    ok, _ = g.check_request("foo", {})
    assert ok is True
    ok, _ = g.check_request("baz", {})
    assert ok is False

def test_guardian_no_allowlist():
    if "GUARDIAN_ALLOW_TOOLS" in os.environ:
        del os.environ["GUARDIAN_ALLOW_TOOLS"]
    g = Guardian()
    ok, _ = g.check_request("any_tool", {})
    assert ok is True

def test_guardian_redact_outputs():
    os.environ["GUARDIAN_REDACT_OUTPUTS"] = "true"
    g = Guardian()
    result = {"text": "Email a@b.com and SSN 123-45-6789"}
    sanitized = g.sanitize_response("test", result)
    assert "REDACTED" in sanitized["text"]
    assert "a@b.com" not in sanitized["text"]

def test_guardian_no_redact():
    os.environ["GUARDIAN_REDACT_OUTPUTS"] = "false"
    g = Guardian()
    result = {"text": "Email a@b.com and SSN 123-45-6789"}
    sanitized = g.sanitize_response("test", result)
    assert sanitized == result
