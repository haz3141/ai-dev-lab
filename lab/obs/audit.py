"""
Audit Logging for MCP Server

Provides JSONL audit logging with request correlation and PII-safe outputs.
"""

import json
import os
import uuid
import time
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from lab.security.redact import redactor


@dataclass
class AuditEvent:
    """Represents an audit log event."""

    timestamp: str
    request_id: str
    event_type: str
    tool_name: str
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    duration_ms: Optional[float] = None
    error: Optional[str] = None


class AuditLogger:
    """JSONL audit logger with PII redaction and correlation IDs."""

    def __init__(self, log_path: str = None):
        self.log_path = log_path or os.getenv("AUDIT_LOG_PATH", "logs/mcp_audit.jsonl")
        self._ensure_log_directory()

    def _ensure_log_directory(self):
        """Ensure the log directory exists."""
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)

    def _generate_request_id(self) -> str:
        """Generate a unique request ID."""
        return str(uuid.uuid4())

    def _sanitize_data(self, data: Any) -> Any:
        """Sanitize data by redacting PII."""
        if isinstance(data, dict):
            return {k: self._sanitize_data(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._sanitize_data(item) for item in data]
        elif isinstance(data, str):
            redacted, _ = redactor.redact_text(data)
            return redacted
        else:
            return data

    def log_tool_call(
        self,
        tool_name: str,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        start_time: float = None,
        user_id: str = None,
        session_id: str = None,
        error: str = None,
    ) -> str:
        """Log a tool call event."""
        request_id = self._generate_request_id()
        timestamp = datetime.utcnow().isoformat() + "Z"

        # Calculate duration if start_time provided
        duration_ms = None
        if start_time:
            duration_ms = (time.time() - start_time) * 1000

        # Sanitize input and output data
        sanitized_input = self._sanitize_data(input_data)
        sanitized_output = self._sanitize_data(output_data)

        event = AuditEvent(
            timestamp=timestamp,
            request_id=request_id,
            event_type="tool_call",
            tool_name=tool_name,
            input_data=sanitized_input,
            output_data=sanitized_output,
            user_id=user_id,
            session_id=session_id,
            duration_ms=duration_ms,
            error=error,
        )

        self._write_event(event)
        return request_id

    def log_security_event(
        self,
        event_type: str,
        tool_name: str,
        details: Dict[str, Any],
        user_id: str = None,
    ) -> str:
        """Log a security-related event."""
        request_id = self._generate_request_id()
        timestamp = datetime.utcnow().isoformat() + "Z"

        event = AuditEvent(
            timestamp=timestamp,
            request_id=request_id,
            event_type=event_type,
            tool_name=tool_name,
            input_data=details,
            output_data={},
            user_id=user_id,
        )

        self._write_event(event)
        return request_id

    def _write_event(self, event: AuditEvent):
        """Write event to JSONL log file."""
        event_dict = asdict(event)

        with open(self.log_path, "a") as f:
            f.write(json.dumps(event_dict) + "\n")

    def get_recent_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent audit events."""
        events = []

        if not os.path.exists(self.log_path):
            return events

        with open(self.log_path, "r") as f:
            lines = f.readlines()

        # Get last N lines
        recent_lines = lines[-limit:] if len(lines) > limit else lines

        for line in recent_lines:
            if line.strip():
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

        return events

    def get_events_by_request_id(self, request_id: str) -> List[Dict[str, Any]]:
        """Get all events for a specific request ID."""
        events = []

        if not os.path.exists(self.log_path):
            return events

        with open(self.log_path, "r") as f:
            for line in f:
                if line.strip():
                    try:
                        event = json.loads(line)
                        if event.get("request_id") == request_id:
                            events.append(event)
                    except json.JSONDecodeError:
                        continue

        return events

    def get_events_by_tool(
        self, tool_name: str, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get recent events for a specific tool."""
        events = []

        if not os.path.exists(self.log_path):
            return events

        with open(self.log_path, "r") as f:
            lines = f.readlines()

        # Search from most recent
        for line in reversed(
            lines[-limit * 2 :]
        ):  # Look at more lines to find enough matches
            if line.strip():
                try:
                    event = json.loads(line)
                    if event.get("tool_name") == tool_name:
                        events.append(event)
                        if len(events) >= limit:
                            break
                except json.JSONDecodeError:
                    continue

        return list(reversed(events))  # Return in chronological order


# Global audit logger instance
audit_logger = AuditLogger()
