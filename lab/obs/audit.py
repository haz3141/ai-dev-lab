"""
Audit Logging for MCP Server

Provides JSONL audit logging with request correlation and PII-safe outputs.
"""

import gzip
import json
import os
import shutil
import time
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any

from lab.security.redact import redactor


@dataclass
class AuditEvent:
    """Represents an audit log event."""

    timestamp: str
    request_id: str
    event_type: str
    tool_name: str
    input_data: dict[str, Any]
    output_data: dict[str, Any]
    user_id: str | None = None
    session_id: str | None = None
    duration_ms: float | None = None
    error: str | None = None


class AuditLogger:
    """JSONL audit logger with PII redaction, correlation IDs, and daily rotation."""

    def __init__(self, log_path: str = None):
        self.base_log_path = log_path or os.getenv("AUDIT_LOG_PATH", "logs/mcp_audit.jsonl")
        self.retention_days = int(os.getenv("AUDIT_RETENTION_DAYS", "30"))
        self._ensure_log_directory()
        self._current_log_path = self._get_daily_log_path()

    def _ensure_log_directory(self):
        """Ensure the log directory exists."""
        os.makedirs(os.path.dirname(self.base_log_path), exist_ok=True)

    def _get_daily_log_path(self) -> str:
        """Get the current day's log file path."""
        today = datetime.utcnow().strftime("%Y-%m-%d")
        base_name = os.path.splitext(self.base_log_path)[0]
        return f"{base_name}_{today}.jsonl"

    def _rotate_log_if_needed(self):
        """Rotate log file if it's a new day."""
        current_path = self._get_daily_log_path()
        if current_path != self._current_log_path:
            # New day - compress previous day's log if it exists
            self._compress_old_log(self._current_log_path)
            self._current_log_path = current_path
            self._cleanup_old_logs()

    def _compress_old_log(self, log_path: str):
        """Compress a log file if it exists and is older than 7 days."""
        if not os.path.exists(log_path):
            return

        # Check if file is older than 7 days
        file_age = datetime.utcnow() - datetime.fromtimestamp(os.path.getmtime(log_path))
        if file_age.days >= 7:
            compressed_path = f"{log_path}.gz"
            if not os.path.exists(compressed_path):
                with open(log_path, "rb") as f_in:
                    with gzip.open(compressed_path, "wb") as f_out:
                        f_out.writelines(f_in)
                os.remove(log_path)

    def _cleanup_old_logs(self):
        """Remove log files older than retention period."""
        log_dir = os.path.dirname(self.base_log_path)

        for filename in os.listdir(log_dir):
            if filename.startswith(os.path.basename(self.base_log_path).split(".")[0]):
                file_path = os.path.join(log_dir, filename)
                if os.path.isfile(file_path):
                    file_age = datetime.utcnow() - datetime.fromtimestamp(
                        os.path.getmtime(file_path)
                    )
                    if file_age.days > self.retention_days:
                        os.remove(file_path)

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
        input_data: dict[str, Any],
        output_data: dict[str, Any],
        start_time: float = None,
        user_id: str = None,
        session_id: str = None,
        error: str = None,
    ) -> str:
        """Log a tool call event."""
        # Check if we need to rotate the log file
        self._rotate_log_if_needed()

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
        details: dict[str, Any],
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

        with open(self._current_log_path, "a") as f:
            f.write(json.dumps(event_dict) + "\n")

    def get_recent_events(self, limit: int = 100) -> list[dict[str, Any]]:
        """Get recent audit events from all available log files."""
        events = []

        # Get all log files (current and recent)
        log_dir = os.path.dirname(self.base_log_path)
        base_name = os.path.basename(self.base_log_path).split(".")[0]

        # Find all log files (including compressed ones)
        log_files = []
        for filename in os.listdir(log_dir):
            if filename.startswith(base_name) and (
                filename.endswith(".jsonl") or filename.endswith(".jsonl.gz")
            ):
                log_files.append(os.path.join(log_dir, filename))

        # Sort by modification time (newest first)
        log_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)

        # Read events from files until we have enough
        for log_file in log_files:
            if len(events) >= limit:
                break

            try:
                if log_file.endswith(".gz"):
                    with gzip.open(log_file, "rt") as f:
                        lines = f.readlines()
                else:
                    with open(log_file) as f:
                        lines = f.readlines()

                # Process lines in reverse order (newest first)
                for line in reversed(lines):
                    if len(events) >= limit:
                        break
                    if line.strip():
                        try:
                            events.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
            except (FileNotFoundError, gzip.BadGzipFile):
                continue

        # Return in chronological order (oldest first)
        return list(reversed(events))

    def get_events_by_request_id(self, request_id: str) -> list[dict[str, Any]]:
        """Get all events for a specific request ID."""
        events = []

        # Search all log files
        log_dir = os.path.dirname(self.base_log_path)
        base_name = os.path.basename(self.base_log_path).split(".")[0]

        for filename in os.listdir(log_dir):
            if filename.startswith(base_name) and (
                filename.endswith(".jsonl") or filename.endswith(".jsonl.gz")
            ):
                log_file = os.path.join(log_dir, filename)
                try:
                    if log_file.endswith(".gz"):
                        with gzip.open(log_file, "rt") as f:
                            for line in f:
                                if line.strip():
                                    try:
                                        event = json.loads(line)
                                        if event.get("request_id") == request_id:
                                            events.append(event)
                                    except json.JSONDecodeError:
                                        continue
                    else:
                        with open(log_file) as f:
                            for line in f:
                                if line.strip():
                                    try:
                                        event = json.loads(line)
                                        if event.get("request_id") == request_id:
                                            events.append(event)
                                    except json.JSONDecodeError:
                                        continue
                except (FileNotFoundError, gzip.BadGzipFile):
                    continue

        return events

    def get_events_by_tool(self, tool_name: str, limit: int = 100) -> list[dict[str, Any]]:
        """Get recent events for a specific tool."""
        events = []

        # Get all log files (current and recent)
        log_dir = os.path.dirname(self.base_log_path)
        base_name = os.path.basename(self.base_log_path).split(".")[0]

        # Find all log files (including compressed ones)
        log_files = []
        for filename in os.listdir(log_dir):
            if filename.startswith(base_name) and (
                filename.endswith(".jsonl") or filename.endswith(".jsonl.gz")
            ):
                log_files.append(os.path.join(log_dir, filename))

        # Sort by modification time (newest first)
        log_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)

        # Read events from files until we have enough
        for log_file in log_files:
            if len(events) >= limit:
                break

            try:
                if log_file.endswith(".gz"):
                    with gzip.open(log_file, "rt") as f:
                        lines = f.readlines()
                else:
                    with open(log_file) as f:
                        lines = f.readlines()

                # Process lines in reverse order (newest first)
                for line in reversed(lines):
                    if len(events) >= limit:
                        break
                    if line.strip():
                        try:
                            event = json.loads(line)
                            if event.get("tool_name") == tool_name:
                                events.append(event)
                        except json.JSONDecodeError:
                            continue
            except (FileNotFoundError, gzip.BadGzipFile):
                continue

        # Return in chronological order (oldest first)
        return list(reversed(events))


def rotate_and_compress(base_dir="logs/audit", days_to_keep=14, compress=True):
    """Rotate and compress audit logs with retention policy."""
    os.makedirs(base_dir, exist_ok=True)
    files = sorted(
        (f for f in os.listdir(base_dir) if f.startswith("audit-") and f.endswith(".jsonl")),
    )
    if compress:
        for f in files:
            gz = os.path.join(base_dir, f + ".gz")
            p = os.path.join(base_dir, f)
            if not os.path.exists(gz):
                with open(p, "rb") as src, gzip.open(gz, "wb") as dst:
                    shutil.copyfileobj(src, dst)
                os.remove(p)
    # prune old
    keep = set(files[-days_to_keep:])
    for f in os.listdir(base_dir):
        if f.startswith("audit-") and (f.endswith(".jsonl") or f.endswith(".jsonl.gz")):
            path = os.path.join(base_dir, f)
            stem = f.split(".jsonl")[0]  # audit-YYYY-MM-DD
            if stem.replace(".gz", "") not in keep:
                os.remove(path)


# Global audit logger instance
audit_logger = AuditLogger()
