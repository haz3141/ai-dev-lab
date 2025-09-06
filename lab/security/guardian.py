"""
Security Guardian for MCP Server

Provides allowlist-based tool access control and PII redaction capabilities.
"""

import os
import re
from typing import List, Any
from functools import wraps
import logging

logger = logging.getLogger(__name__)


class Guardian:
    """Security guardian for MCP tool access control and PII redaction."""

    def __init__(self):
        self.allowlist = self._load_allowlist()
        self.redact_outputs = (
            os.getenv("GUARDIAN_REDACT_OUTPUTS", "true").lower() == "true"
        )

    def _load_allowlist(self) -> List[str]:
        """Load allowed tools from environment variable."""
        allowlist_str = os.getenv("GUARDIAN_ALLOW_TOOLS", "")
        if not allowlist_str:
            # Default allowlist - only essential tools
            return ["health", "tools/summarize"]

        return [tool.strip() for tool in allowlist_str.split(",") if tool.strip()]

    def is_tool_allowed(self, tool_name: str) -> bool:
        """Check if a tool is allowed by the guardian."""
        return tool_name in self.allowlist

    def guard_tool(self, tool_name: str):
        """Decorator to guard MCP tool endpoints."""

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                if not self.is_tool_allowed(tool_name):
                    logger.warning(f"Blocked access to unauthorized tool: {tool_name}")
                    return {
                        "error": "Unauthorized",
                        "message": f"Tool '{tool_name}' is not allowed by security policy",
                    }

                try:
                    result = func(*args, **kwargs)
                    if self.redact_outputs:
                        return self._redact_output(result)
                    else:
                        return result
                except Exception as e:
                    logger.error(f"Error in guarded tool {tool_name}: {e}")
                    return {
                        "error": "Internal error",
                        "message": "An error occurred processing the request",
                    }

            return wrapper

        return decorator

    def _redact_output(self, data: Any) -> Any:
        """Recursively redact PII from output data."""
        if not self.redact_outputs:
            return data

        if isinstance(data, dict):
            return {k: self._redact_output(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._redact_output(item) for item in data]
        elif isinstance(data, str):
            return self._redact_string(data)
        else:
            return data

    def _redact_string(self, text: str) -> str:
        """Redact PII patterns from text."""
        # SSN pattern (XXX-XX-XXXX)
        text = re.sub(r"\b\d{3}-\d{2}-\d{4}\b", "[REDACTED-SSN]", text)

        # Credit card pattern (XXXX-XXXX-XXXX-XXXX)
        text = re.sub(r"\b\d{4}-\d{4}-\d{4}-\d{4}\b", "[REDACTED-CC]", text)

        # Email pattern
        text = re.sub(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "[REDACTED-EMAIL]",
            text,
        )

        # Phone number pattern
        text = re.sub(r"\b\d{3}-\d{3}-\d{4}\b", "[REDACTED-PHONE]", text)

        return text


# Global guardian instance
guardian = Guardian()
