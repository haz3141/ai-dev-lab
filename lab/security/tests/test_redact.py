from lab.security.redact import redact

def test_redact_basic():
    txt = "Email a@b.com and SSN 123-45-6789 and card 4242424242424242"
    red, n = redact(txt)
    assert n >= 2
    assert "REDACTED" in red
    assert "a@b.com" not in red
    assert "123-45-6789" not in red
    assert "4242424242424242" not in red

def test_redact_no_pii():
    txt = "This is a normal text with no PII"
    red, n = redact(txt)
    assert n == 0
    assert red == txt

def test_redact_multiple_emails():
    txt = "Contact john@example.com or jane@test.org for more info"
    red, n = redact(txt)
    assert n == 2
    assert "REDACTED-EMAIL" in red
    assert "john@example.com" not in red
    assert "jane@test.org" not in red
