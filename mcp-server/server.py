from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Lab MCP Server (skeleton)")

class SearchRequest(BaseModel):
    query: str

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/tools/search_docs")
def search_docs(req: SearchRequest):
    return {"query": req.query, "results": []}
