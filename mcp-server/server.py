from fastapi import FastAPI
from pydantic import BaseModel
from lab.dsp.summarize import Summarize
from lab.rag.ingest import load_texts
from lab.rag.chunk import chunk_records
from lab.rag.retrieve import BM25Retriever
import os

app = FastAPI(title="Lab MCP Server (skeleton)")

class SearchRequest(BaseModel):
    query: str

class SummarizeRequest(BaseModel):
    passage: str

class RetrieveRequest(BaseModel):
    query: str
    k: int = 3

summarizer = Summarize()

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/tools/search_docs")
def search_docs(req: SearchRequest):
    return {"query": req.query, "results": []}

@app.post("/tools/summarize")
def summarize(req: SummarizeRequest):
    return {"summary": summarizer(req.passage)}

@app.post("/tools/retrieve")
def retrieve(req: RetrieveRequest):
    data_dir = os.getenv("RAG_DATA_DIR", "lab/rag/fixtures")
    records = list(load_texts(data_dir))
    chunks = chunk_records(records, max_chars=200)
    retriever = BM25Retriever(chunks)
    hits = retriever.query(req.query, k=req.k)
    return {"hits": hits, "k": req.k, "count": len(hits), "data_dir": data_dir}
