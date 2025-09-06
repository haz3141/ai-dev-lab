from fastapi import FastAPI, Request
from pydantic import BaseModel
import time
import logging
from lab.dsp.summarize import Summarize
from lab.security.guardian import guardian
from lab.obs.audit import audit_logger

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


@app.post("/tools/search_docs")
@guardian.guard_tool("tools/search_docs")
def search_docs(req: SearchRequest, request: Request):
    """Search documents endpoint - guarded by security policy."""
    start_time = time.time()
    user_id = request.headers.get("X-User-ID")
    session_id = request.headers.get("X-Session-ID")

    try:
        # Mock search results for now
        results = []

        # Log the tool call
        request_id = audit_logger.log_tool_call(
            tool_name="tools/search_docs",
            input_data={"query": req.query},
            output_data={"query": req.query, "results": results},
            start_time=start_time,
            user_id=user_id,
            session_id=session_id,
        )

        return {"query": req.query, "results": results, "request_id": request_id}
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
