from __future__ import annotations
import re
from typing import Tuple

PII_PATTERNS = [
    (r"\b\d{3}-\d{2}-\d{4}\b", "[REDACTED-SSN]"),
    (r"\b\d{13,19}\b", "[REDACTED-CC]"),
    (r"\b[\w\.-]+@[\w\.-]+\.\w{2,}\b", "[REDACTED-EMAIL]"),
]

def redact(text: str) -> Tuple[str, int]:
    """
    Redact PII patterns from text.
    
    Args:
        text: Input text to redact
        
    Returns:
        Tuple of (redacted_text, number_of_replacements)
    """
    replaced = 0
    for pattern, token in PII_PATTERNS:
        new_text, n = re.subn(pattern, token, text)
        replaced += n
        text = new_text
    return text, replaced
