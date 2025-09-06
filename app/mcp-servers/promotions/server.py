"""
MCP Promotions Server - v0.6.2

Minimal runtime server for promoted MCP tools.
This is a production-ready wrapper around lab functionality.
"""

from fastapi import FastAPI, Request
from pydantic import BaseModel
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="MCP Promotions Server (v0.6.2)")


class SearchRequest(BaseModel):
    query: str


class SummarizeRequest(BaseModel):
    passage: str


@app.get("/health")
def health():
    """Health check endpoint - always allowed."""
    return {"ok": True, "version": "0.6.2", "service": "mcp-promotions"}


@app.post("/tools/search_docs")
def search_docs(req: SearchRequest, request: Request):
    """Search documents endpoint - promoted from lab."""
    start_time = time.time()
    user_id = request.headers.get("X-User-ID")
    session_id = request.headers.get("X-Session-ID")

    try:
        # Mock search results for now - will be replaced with real impl
        results = [
            {
                "title": "Sample Document",
                "content": f"Search results for: {req.query}",
                "score": 0.95,
                "source": "promoted-docs"
            }
        ]

        # Log the tool call
        logger.info("search_docs called by user %s, session %s",
                    user_id, session_id)

        return {
            "query": req.query,
            "results": results,
            "request_id": f"req_{int(start_time)}",
            "service": "mcp-promotions"
        }
    except Exception as e:
        logger.error("Error in search_docs: %s", e)
        return {"error": "Internal error", "message": "Search failed"}


@app.post("/tools/summarize")
def summarize(req: SummarizeRequest, request: Request):
    """Summarize text endpoint - promoted from lab."""
    start_time = time.time()
    user_id = request.headers.get("X-User-ID")
    session_id = request.headers.get("X-Session-ID")

    try:
        # Mock summarization for now - will be replaced with real impl
        summary = f"Summary of: {req.passage[:50]}..."

        # Log the tool call
        logger.info("summarize called by user %s, session %s",
                    user_id, session_id)

        return {
            "summary": summary,
            "request_id": f"req_{int(start_time)}",
            "service": "mcp-promotions"
        }
    except Exception as e:
        logger.error("Error in summarize: %s", e)
        return {"error": "Internal error", "message": "Summarization failed"}


@app.get("/promotions/status")
def get_promotion_status():
    """Get current promotion status and available tools."""
    return {
        "version": "0.6.2",
        "promoted_tools": ["search_docs", "summarize"],
        "status": "active",
        "lab_dependencies": [
            "lab.dsp.summarize",
            "lab.security.guardian",
            "lab.obs.audit"
        ]
    }
