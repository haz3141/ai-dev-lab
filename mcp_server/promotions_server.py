# mcp_server/promotions_server.py
"""MCP Promotions Server - v0.6.4

MCP-compatible server for promoted lab tools.
This wraps the lab functionality in MCP protocol.
"""

import json
import time
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from lab.dsp.summarize import Summarize
from lab.obs.audit import audit_logger
from lab.security.guardian import guardian

# Create the MCP app
app = FastMCP(name="mcp-promotions")

# Initialize lab components
summarizer = Summarize()


@app.tool()
def search_docs(query: str, root: str = ".", max_results: int = 5) -> dict:
    """Search documents with security guardrails.

    Args:
        query: Search query string
        root: Root directory to search (default: ".")
        max_results: Maximum number of results to return (default: 5)

    Returns:
        Dictionary with matches array containing file, line, and text
    """
    # Apply security guardrails
    if not guardian.is_tool_allowed("search_docs"):
        return {"error": "Tool not allowed by security policy"}

    start_time = time.time()

    try:
        q = (query or "").strip().lower()
        if not q:
            return {"matches": []}

        matches, exts = [], {".md", ".txt", ".py"}
        for p in Path(root).rglob("*"):
            if p.is_file() and p.suffix in exts and p.stat().st_size <= 256_000:
                try:
                    for i, line in enumerate(p.read_text(errors="ignore").splitlines(), 1):
                        if q in line.lower():
                            matches.append({"file": str(p), "line": i, "text": line.strip()})
                            if len(matches) >= max_results:
                                break
                    if len(matches) >= max_results:
                        break
                except OSError:
                    continue

        # Log the tool call
        request_id = audit_logger.log_tool_call(
            tool_name="search_docs",
            input_data={"query": query, "root": root, "max_results": max_results},
            output_data={"matches": matches},
            start_time=start_time,
            user_id="mcp-client",
            session_id="mcp-session",
        )

        return {"matches": matches, "request_id": request_id}

    except Exception as e:
        audit_logger.log_tool_call(
            tool_name="search_docs",
            input_data={"query": query, "root": root, "max_results": max_results},
            output_data={},
            start_time=start_time,
            user_id="mcp-client",
            session_id="mcp-session",
            error=str(e),
        )
        return {"error": "Search failed", "message": str(e)}


@app.tool()
def summarize(text: str, max_sentences: int = 3) -> dict:
    """Summarize text using lab summarization.

    Args:
        text: Text to summarize
        max_sentences: Maximum number of sentences in summary (default: 3)

    Returns:
        Dictionary with summary text
    """
    # Apply security guardrails
    if not guardian.is_tool_allowed("summarize"):
        return {"error": "Tool not allowed by security policy"}

    start_time = time.time()

    try:
        summary = summarizer(text)

        # Log the tool call
        request_id = audit_logger.log_tool_call(
            tool_name="summarize",
            input_data={"text": text, "max_sentences": max_sentences},
            output_data={"summary": summary},
            start_time=start_time,
            user_id="mcp-client",
            session_id="mcp-session",
        )

        return {"summary": summary, "request_id": request_id}

    except Exception as e:
        audit_logger.log_tool_call(
            tool_name="summarize",
            input_data={"text": text, "max_sentences": max_sentences},
            output_data={},
            start_time=start_time,
            user_id="mcp-client",
            session_id="mcp-session",
            error=str(e),
        )
        return {"error": "Summarization failed", "message": str(e)}


@app.tool()
def summarize_eval(run_dir: str) -> dict:
    """Summarize evaluation results from a run directory.

    Args:
        run_dir: Path to evaluation run directory

    Returns:
        Dictionary with evaluation summary and metrics
    """
    # Apply security guardrails
    if not guardian.is_tool_allowed("summarize_eval"):
        return {"error": "Tool not allowed by security policy"}

    start_time = time.time()

    try:
        metrics_file = Path(run_dir) / "metrics.json"
        if not metrics_file.exists():
            return {"status": "error", "message": "No metrics.json found"}

        with open(metrics_file) as f:
            metrics = json.load(f)

        # Extract key metrics
        retrieval = metrics.get("retrieval", {})
        answer = metrics.get("answer", {})
        judge = metrics.get("judge", {})
        faithfulness = metrics.get("faithfulness", {})
        context = metrics.get("context", {})
        perf = metrics.get("perf", {})

        # Determine pass/fail status
        passed = (
            retrieval.get("recall_at_5", 0) >= 0.85
            and retrieval.get("recall_at_10", 0) >= 0.92
            and retrieval.get("mrr_at_10", 0) >= 0.60
            and answer.get("f1", 0) >= 0.55
            and judge.get("pass_rate", 0) >= 0.80
            and faithfulness.get("hallucination_rate", 1) <= 0.05
            and context.get("utilization_rate", 0) >= 0.90
            and perf.get("p95_s", 999) <= 3.5
        )

        status = "PASS" if passed else "FAIL"

        summary = f"RAG Gates {status}: R@5={retrieval.get('recall_at_5', 0):.2f}, R@10={retrieval.get('recall_at_10', 0):.2f}, MRR@10={retrieval.get('mrr_at_10', 0):.2f}, F1={answer.get('f1', 0):.2f}, Judge={judge.get('pass_rate', 0):.2f}, Halluc={faithfulness.get('hallucination_rate', 0):.2f}, Context={context.get('utilization_rate', 0):.2f}, P95={perf.get('p95_s', 0):.1f}s"

        result = {
            "status": status,
            "summary": summary,
            "metrics": {
                "retrieval": retrieval,
                "answer": answer,
                "judge": judge,
                "faithfulness": faithfulness,
                "context": context,
                "perf": perf,
            },
        }

        # Log the tool call
        request_id = audit_logger.log_tool_call(
            tool_name="summarize_eval",
            input_data={"run_dir": run_dir},
            output_data=result,
            start_time=start_time,
            user_id="mcp-client",
            session_id="mcp-session",
        )

        result["request_id"] = request_id
        return result

    except Exception as e:
        audit_logger.log_tool_call(
            tool_name="summarize_eval",
            input_data={"run_dir": run_dir},
            output_data={},
            start_time=start_time,
            user_id="mcp-client",
            session_id="mcp-session",
            error=str(e),
        )
        return {"status": "error", "message": str(e)}


@app.tool()
def get_promotion_status() -> dict:
    """Get current promotion status and available tools.

    Returns:
        Dictionary with promotion status and tool information
    """
    return {
        "version": "0.6.4",
        "promoted_tools": ["search_docs", "summarize", "summarize_eval"],
        "status": "active",
        "lab_dependencies": [
            "lab.dsp.summarize",
            "lab.security.guardian",
            "lab.obs.audit",
        ],
    }


if __name__ == "__main__":
    # Run as MCP server with stdio transport
    app.run(transport="stdio")
