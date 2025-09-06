from fastapi import FastAPI
from pydantic import BaseModel
from lab.dsp.summarize import Summarize

app = FastAPI(title="Lab MCP Server (skeleton)")

class SearchRequest(BaseModel):
    query: str

class SummarizeRequest(BaseModel):
    passage: str

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
