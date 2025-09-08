import logging
import time

from fastapi import FastAPI, Request
from pydantic import BaseModel

from lab.dsp.summarize import Summarize
from lab.obs.audit import audit_logger
from lab.security.guardian import guardian
from mcp_server.tools.terminal_helper import (
    check_file_exists,
    check_gates_safe,
    list_directory_safe,
    read_file_safe,
    run_command,
    run_eval_safe,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Lab MCP Server (v0.6.4)")


class SearchRequest(BaseModel):
    query: str


class SummarizeRequest(BaseModel):
    passage: str


class TerminalCommandRequest(BaseModel):
    command: str
    timeout: int = 30
    cwd: str = None


class FileCheckRequest(BaseModel):
    filepath: str


class FileReadRequest(BaseModel):
    filepath: str
    max_lines: int = 100


class DirectoryListRequest(BaseModel):
    directory: str
    max_items: int = 50


class EvalRunRequest(BaseModel):
    dataset: str
    output_dir: str
    timeout: int = 300


class GatesCheckRequest(BaseModel):
    metrics_file: str


summarizer = Summarize()


@app.get("/health")
def health():
    """Health check endpoint - always allowed."""
    return {"ok": True, "version": "0.6.4"}


@app.get("/healthz")
def healthz():
    """Health check endpoint for Kubernetes/CI - always allowed."""
    return {"ok": True, "version": "0.6.4"}


@app.get("/")
def root():
    """Root endpoint - always allowed."""
    return {"ok": True, "version": "0.6.4", "message": "Lab MCP Server"}


@app.post("/tools/search_docs")
@guardian.guard_tool("tools/search_docs")
def search_docs(req: SearchRequest, request: Request):
    """Search documents endpoint - guarded by security policy."""
    start_time = time.time()
    user_id = request.headers.get("X-User-ID")
    session_id = request.headers.get("X-Session-ID")

    try:
        # Simple search implementation
        from pathlib import Path

        q = (req.query or "").strip().lower()
        if not q:
            search_result = {"matches": []}
        else:
            matches, exts = [], {".md", ".txt", ".py"}
            for p in Path(".").rglob("*"):
                if p.is_file() and p.suffix in exts and p.stat().st_size <= 256_000:
                    try:
                        for i, line in enumerate(p.read_text(errors="ignore").splitlines(), 1):
                            if q in line.lower():
                                matches.append({"file": str(p), "line": i, "text": line.strip()})
                                if len(matches) >= 5:
                                    break
                        if len(matches) >= 5:
                            break
                    except OSError:
                        continue
            search_result = {"matches": matches}
        # Log the tool call
        request_id = audit_logger.log_tool_call(
            tool_name="tools/search_docs",
            input_data={"query": req.query},
            output_data=search_result,
            start_time=start_time,
            user_id=user_id,
            session_id=session_id,
        )

        # Add request_id to response
        search_result["request_id"] = request_id
        return search_result
    except Exception as e:
        logger.error(f"Error in search_docs: {e}")
        audit_logger.log_tool_call(
            tool_name="tools/search_docs",
            input_data={"query": req.query},
            output_data={},
            start_time=start_time,
            user_id=user_id,
            session_id=session_id,
            error=str(e),
        )
        return {"error": "Internal error", "message": "Search failed"}


@app.post("/tools/summarize")
@guardian.guard_tool("tools/summarize")
def summarize(req: SummarizeRequest, request: Request):
    """Summarize text endpoint - guarded by security policy."""
    start_time = time.time()
    user_id = request.headers.get("X-User-ID")
    session_id = request.headers.get("X-Session-ID")

    try:
        summary = summarizer(req.passage)

        # Log the tool call
        request_id = audit_logger.log_tool_call(
            tool_name="tools/summarize",
            input_data={"passage": req.passage},
            output_data={"summary": summary},
            start_time=start_time,
            user_id=user_id,
            session_id=session_id,
        )

        return {"summary": summary, "request_id": request_id}
    except Exception as e:
        logger.error(f"Error in summarize: {e}")
        audit_logger.log_tool_call(
            tool_name="tools/summarize",
            input_data={"passage": req.passage},
            output_data={},
            start_time=start_time,
            user_id=user_id,
            session_id=session_id,
            error=str(e),
        )
        return {"error": "Internal error", "message": "Summarization failed"}


@app.get("/audit/recent")
def get_recent_audit_events(limit: int = 100):
    """Get recent audit events (admin endpoint)."""
    return audit_logger.get_recent_events(limit)


@app.get("/audit/request/{request_id}")
def get_audit_events_by_request(request_id: str):
    """Get audit events for a specific request ID."""
    return audit_logger.get_events_by_request_id(request_id)


@app.get("/audit/tool/{tool_name}")
def get_audit_events_by_tool(tool_name: str, limit: int = 100):
    """Get audit events for a specific tool."""
    return audit_logger.get_events_by_tool(tool_name, limit)


# Terminal Helper Endpoints
@app.post("/tools/run_command")
@guardian.guard_tool("tools/run_command")
def run_terminal_command(req: TerminalCommandRequest, request: Request):
    """Run a terminal command safely with timeout."""
    start_time = time.time()
    user_id = request.headers.get("X-User-ID")
    session_id = request.headers.get("X-Session-ID")

    try:
        result = run_command(req.command, req.timeout, req.cwd)

        # Log the tool call
        request_id = audit_logger.log_tool_call(
            tool_name="tools/run_command",
            input_data={"command": req.command, "timeout": req.timeout, "cwd": req.cwd},
            output_data=result,
            start_time=start_time,
            user_id=user_id,
            session_id=session_id,
        )

        result["request_id"] = request_id
        return result
    except Exception as e:
        logger.error(f"Error in run_command: {e}")
        audit_logger.log_tool_call(
            tool_name="tools/run_command",
            input_data={"command": req.command, "timeout": req.timeout, "cwd": req.cwd},
            output_data={},
            start_time=start_time,
            user_id=user_id,
            session_id=session_id,
            error=str(e),
        )
        return {"error": "Internal error", "message": "Command execution failed"}


@app.post("/tools/check_file")
@guardian.guard_tool("tools/check_file")
def check_file_endpoint(req: FileCheckRequest, request: Request):
    """Check if a file exists and get its info."""
    start_time = time.time()
    user_id = request.headers.get("X-User-ID")
    session_id = request.headers.get("X-Session-ID")

    try:
        result = check_file_exists(req.filepath)

        # Log the tool call
        request_id = audit_logger.log_tool_call(
            tool_name="tools/check_file",
            input_data={"filepath": req.filepath},
            output_data=result,
            start_time=start_time,
            user_id=user_id,
            session_id=session_id,
        )

        result["request_id"] = request_id
        return result
    except Exception as e:
        logger.error(f"Error in check_file: {e}")
        audit_logger.log_tool_call(
            tool_name="tools/check_file",
            input_data={"filepath": req.filepath},
            output_data={},
            start_time=start_time,
            user_id=user_id,
            session_id=session_id,
            error=str(e),
        )
        return {"error": "Internal error", "message": "File check failed"}


@app.post("/tools/read_file")
@guardian.guard_tool("tools/read_file")
def read_file_endpoint(req: FileReadRequest, request: Request):
    """Safely read a file with line limit."""
    start_time = time.time()
    user_id = request.headers.get("X-User-ID")
    session_id = request.headers.get("X-Session-ID")

    try:
        result = read_file_safe(req.filepath, req.max_lines)

        # Log the tool call
        request_id = audit_logger.log_tool_call(
            tool_name="tools/read_file",
            input_data={"filepath": req.filepath, "max_lines": req.max_lines},
            output_data=result,
            start_time=start_time,
            user_id=user_id,
            session_id=session_id,
        )

        result["request_id"] = request_id
        return result
    except Exception as e:
        logger.error(f"Error in read_file: {e}")
        audit_logger.log_tool_call(
            tool_name="tools/read_file",
            input_data={"filepath": req.filepath, "max_lines": req.max_lines},
            output_data={},
            start_time=start_time,
            user_id=user_id,
            session_id=session_id,
            error=str(e),
        )
        return {"error": "Internal error", "message": "File read failed"}


@app.post("/tools/list_directory")
@guardian.guard_tool("tools/list_directory")
def list_directory_endpoint(req: DirectoryListRequest, request: Request):
    """Safely list directory contents with limit."""
    start_time = time.time()
    user_id = request.headers.get("X-User-ID")
    session_id = request.headers.get("X-Session-ID")

    try:
        result = list_directory_safe(req.directory, req.max_items)

        # Log the tool call
        request_id = audit_logger.log_tool_call(
            tool_name="tools/list_directory",
            input_data={"directory": req.directory, "max_items": req.max_items},
            output_data=result,
            start_time=start_time,
            user_id=user_id,
            session_id=session_id,
        )

        result["request_id"] = request_id
        return result
    except Exception as e:
        logger.error(f"Error in list_directory: {e}")
        audit_logger.log_tool_call(
            tool_name="tools/list_directory",
            input_data={"directory": req.directory, "max_items": req.max_items},
            output_data={},
            start_time=start_time,
            user_id=user_id,
            session_id=session_id,
            error=str(e),
        )
        return {"error": "Internal error", "message": "Directory listing failed"}


@app.post("/tools/run_eval")
@guardian.guard_tool("tools/run_eval")
def run_eval_endpoint(req: EvalRunRequest, request: Request):
    """Safely run evaluation with proper error handling."""
    start_time = time.time()
    user_id = request.headers.get("X-User-ID")
    session_id = request.headers.get("X-Session-ID")

    try:
        result = run_eval_safe(req.dataset, req.output_dir, req.timeout)

        # Log the tool call
        request_id = audit_logger.log_tool_call(
            tool_name="tools/run_eval",
            input_data={
                "dataset": req.dataset,
                "output_dir": req.output_dir,
                "timeout": req.timeout,
            },
            output_data=result,
            start_time=start_time,
            user_id=user_id,
            session_id=session_id,
        )

        result["request_id"] = request_id
        return result
    except Exception as e:
        logger.error(f"Error in run_eval: {e}")
        audit_logger.log_tool_call(
            tool_name="tools/run_eval",
            input_data={
                "dataset": req.dataset,
                "output_dir": req.output_dir,
                "timeout": req.timeout,
            },
            output_data={},
            start_time=start_time,
            user_id=user_id,
            session_id=session_id,
            error=str(e),
        )
        return {"error": "Internal error", "message": "Evaluation failed"}


@app.post("/tools/check_gates")
@guardian.guard_tool("tools/check_gates")
def check_gates_endpoint(req: GatesCheckRequest, request: Request):
    """Safely check if gates pass using metrics file."""
    start_time = time.time()
    user_id = request.headers.get("X-User-ID")
    session_id = request.headers.get("X-Session-ID")

    try:
        result = check_gates_safe(req.metrics_file)

        # Log the tool call
        request_id = audit_logger.log_tool_call(
            tool_name="tools/check_gates",
            input_data={"metrics_file": req.metrics_file},
            output_data=result,
            start_time=start_time,
            user_id=user_id,
            session_id=session_id,
        )

        result["request_id"] = request_id
        return result
    except Exception as e:
        logger.error(f"Error in check_gates: {e}")
        audit_logger.log_tool_call(
            tool_name="tools/check_gates",
            input_data={"metrics_file": req.metrics_file},
            output_data={},
            start_time=start_time,
            user_id=user_id,
            session_id=session_id,
            error=str(e),
        )
        return {"error": "Internal error", "message": "Gate check failed"}
