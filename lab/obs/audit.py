from __future__ import annotations
import json, os, time, uuid
from typing import Any, Dict

LOG_PATH = os.getenv("AUDIT_LOG_PATH", "logs/mcp_audit.jsonl")

def log_event(kind: str, tool: str, payload: Dict[str, Any], result: Dict[str, Any], ok: bool, msg: str = "") -> None:
    """
    Log an audit event to JSONL file.
    
    Args:
        kind: Type of event (e.g., "tool_call")
        tool: Name of the tool
        payload: Request payload
        result: Response result
        ok: Whether the operation succeeded
        msg: Optional message
    """
    evt = {
        "ts": time.time(),
        "req_id": str(uuid.uuid4()),
        "kind": kind,
        "tool": tool,
        "ok": ok,
        "msg": msg,
        "payload": payload,
        "result": result,
    }
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(evt) + "\n")
