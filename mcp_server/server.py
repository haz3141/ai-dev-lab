import logging
import time

from fastapi import FastAPI, Request
from pydantic import BaseModel

from lab.dsp.summarize import Summarize
from lab.obs.audit import audit_logger
from lab.security.guardian import guardian
from mcp_server.tools.search_docs import search_documents_endpoint

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Lab MCP Server (v0.6.0)")


class SearchRequest(BaseModel):
    query: str


class SummarizeRequest(BaseModel):
    passage: str


summarizer = Summarize()


@app.get("/health")
def health():
    """Health check endpoint - always allowed."""
    return {"ok": True, "version": "0.6.0"}


@app.get("/healthz")
def healthz():
    """Health check endpoint for Kubernetes/CI - always allowed."""
    return {"ok": True, "version": "0.6.0"}


@app.get("/")
def root():
    """Root endpoint - always allowed."""
    return {"ok": True, "version": "0.6.0", "message": "Lab MCP Server"}


@app.post("/tools/search_docs")
@guardian.guard_tool("tools/search_docs")
def search_docs(req: SearchRequest, request: Request):
    """Search documents endpoint - guarded by security policy."""
    start_time = time.time()
    user_id = request.headers.get("X-User-ID")
    session_id = request.headers.get("X-Session-ID")

    try:
        # Use the real search tool
        search_result = search_documents_endpoint(req.query, top_k=5)
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
