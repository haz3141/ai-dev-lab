"""
PII Redaction Utilities

Provides comprehensive PII detection and redaction capabilities.
"""

import re
from typing import List, Dict, Tuple
from dataclasses import dataclass

@dataclass
class PIIMatch:
    """Represents a PII match with type and position."""
    pii_type: str
    start: int
    end: int
    original: str
    redacted: str

class PIIRedactor:
    """Comprehensive PII redaction utility."""
    
    def __init__(self):
        self.patterns = {
            'ssn': [
                r'\b\d{3}-\d{2}-\d{4}\b',  # XXX-XX-XXXX
                r'\b\d{3}\s\d{2}\s\d{4}\b',  # XXX XX XXXX
                r'\b\d{9}\b'  # XXXXXXXXX (9 consecutive digits)
            ],
            'credit_card': [
                r'\b\d{4}-\d{4}-\d{4}-\d{4}\b',  # XXXX-XXXX-XXXX-XXXX
                r'\b\d{4}\s\d{4}\s\d{4}\s\d{4}\b',  # XXXX XXXX XXXX XXXX
                r'\b\d{13,19}\b'  # 13-19 consecutive digits
            ],
            'email': [
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            ],
            'phone': [
                r'\b\d{3}-\d{3}-\d{4}\b',  # XXX-XXX-XXXX
                r'\(\d{3}\)\s\d{3}-\d{4}',  # (XXX) XXX-XXXX
                r'\b\d{3}\.\d{3}\.\d{4}\b',  # XXX.XXX.XXXX
                r'\b\d{10}\b',  # XXXXXXXXXX
                r'\b\d{3}\s\d{3}\s\d{4}\b'  # XXX XXX XXXX
            ],
            'ip_address': [
                r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'  # IPv4
            ]
        }
    
    def find_pii(self, text: str) -> List[PIIMatch]:
        """Find all PII matches in text."""
        matches = []
        
        for pii_type, patterns in self.patterns.items():
            for pattern in patterns:
                for match in re.finditer(pattern, text, re.IGNORECASE):
                    matches.append(PIIMatch(
                        pii_type=pii_type,
                        start=match.start(),
                        end=match.end(),
                        original=match.group(),
                        redacted=f'[REDACTED-{pii_type.upper()}]'
                    ))
        
        # Sort by position for proper redaction
        matches.sort(key=lambda x: x.start)
        return matches
    
    def redact_text(self, text: str) -> Tuple[str, List[PIIMatch]]:
        """Redact PII from text and return redacted text with match info."""
        matches = self.find_pii(text)
        
        if not matches:
            return text, []
        
        # Redact from end to start to maintain positions
        redacted = text
        for match in reversed(matches):
            redacted = redacted[:match.start] + match.redacted + redacted[match.end:]
        
        return redacted, matches
    
    def get_redaction_summary(self, matches: List[PIIMatch]) -> Dict[str, int]:
        """Get summary of redacted PII types."""
        summary = {}
        for match in matches:
            summary[match.pii_type] = summary.get(match.pii_type, 0) + 1
        return summary

# Global redactor instance
redactor = PIIRedactor()
