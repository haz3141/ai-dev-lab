from __future__ import annotations
import os
from typing import Dict, Any, Tuple
from lab.security.redact import redact

class Guardian:
    """
    Lightweight request/response guardian:
    - allowlist tools via GUARDIAN_ALLOW_TOOLS="tool1,tool2"
    - redact response bodies when GUARDIAN_REDACT_OUTPUTS=true
    """
    def __init__(self):
        allow = os.getenv("GUARDIAN_ALLOW_TOOLS", "").strip()
        self.allowlist = {t.strip() for t in allow.split(",")} if allow else set()
        self.redact_outputs = os.getenv("GUARDIAN_REDACT_OUTPUTS", "true").lower() == "true"

    def check_request(self, tool_name: str, payload: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Check if a tool request is allowed.
        
        Args:
            tool_name: Name of the tool being called
            payload: Request payload
            
        Returns:
            Tuple of (is_allowed, reason)
        """
        if self.allowlist and tool_name not in self.allowlist:
            return False, f"Tool '{tool_name}' not allowed by guardian."
        return True, "ok"

    def sanitize_response(self, tool_name: str, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize response by redacting PII if enabled.
        
        Args:
            tool_name: Name of the tool
            result: Response result to sanitize
            
        Returns:
            Sanitized result
        """
        if not self.redact_outputs:
            return result
        # naive pass: redact all string fields
        def _scrub(v):
            if isinstance(v, str):
                red, _ = redact(v)
                return red
            if isinstance(v, list):
                return [_scrub(x) for x in v]
            if isinstance(v, dict):
                return {k: _scrub(x) for k, x in v.items()}
            return v
        return _scrub(result)
