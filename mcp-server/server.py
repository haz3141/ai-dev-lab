from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from lab.dsp.summarize import Summarize
from lab.rag.ingest import load_texts
from lab.rag.chunk import chunk_records
from lab.rag.retrieve import BM25Retriever
from lab.rag.hybrid import HybridRetriever
from lab.security.guardian import Guardian
from lab.obs.audit import log_event
import os

app = FastAPI(title="Lab MCP Server (skeleton)")

# Initialize Guardian for security
GUARD = Guardian()

def guard_and_log(tool_name: str, req, func):
    """Helper function to guard tool calls and log them."""
    # Extract request payload
    payload = req.model_dump() if hasattr(req, 'model_dump') else {}
    
    # Check if tool is allowed
    ok, why = GUARD.check_request(tool_name, payload)
    if not ok:
        log_event("tool_call", tool_name, payload, {"error": why}, False, why)
        raise HTTPException(status_code=403, detail=why)
    
    try:
        # Execute the function
        result = func()
        # Sanitize response
        sanitized_result = GUARD.sanitize_response(tool_name, result)
        # Log successful call
        log_event("tool_call", tool_name, payload, sanitized_result, True)
        return sanitized_result
    except Exception as e:
        # Log failed call
        log_event("tool_call", tool_name, payload, {"error": str(e)}, False, "exception")
        raise


class SearchRequest(BaseModel):
    query: str


class SummarizeRequest(BaseModel):
    passage: str


class RetrieveRequest(BaseModel):
    query: str
    k: int = 3


class RetrieveHybridRequest(BaseModel):
    query: str
    k: int = 5
    alpha: float | None = None


summarizer = Summarize()

@app.get("/health")
def health():
    return {"ok": True}


@app.post("/tools/search_docs")
def search_docs(req: SearchRequest):
    def _search():
        return {"query": req.query, "results": []}
    return guard_and_log("search_docs", req, _search)


@app.post("/tools/summarize")
def summarize(req: SummarizeRequest):
    def _summarize():
        return {"summary": summarizer(req.passage)}
    return guard_and_log("summarize", req, _summarize)


@app.post("/tools/retrieve")
def retrieve(req: RetrieveRequest):
    def _retrieve():
        data_dir = os.getenv("RAG_DATA_DIR", "lab/rag/fixtures")
        records = list(load_texts(data_dir))
        chunks = chunk_records(records, max_chars=200)
        retriever = BM25Retriever(chunks)
        hits = retriever.query(req.query, k=req.k)
        return {"hits": hits, "k": req.k, "count": len(hits), "data_dir": data_dir}
    return guard_and_log("retrieve", req, _retrieve)


@app.post("/tools/retrieve_hybrid")
def retrieve_hybrid(req: RetrieveHybridRequest):
    def _retrieve_hybrid():
        data_dir = os.getenv("RAG_DATA_DIR", "lab/rag/fixtures")
        records = list(load_texts(data_dir))
        chunks = chunk_records(records, max_chars=200)
        hr = HybridRetriever(chunks, alpha=req.alpha)
        hits = hr.query(req.query, k=req.k)
        return {"hits": hits, "k": req.k, "alpha": hr.alpha,
                "count": len(hits), "data_dir": data_dir}
    return guard_and_log("retrieve_hybrid", req, _retrieve_hybrid)
