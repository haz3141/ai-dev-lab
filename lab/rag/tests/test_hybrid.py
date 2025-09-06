import os

from lab.rag.ingest import load_texts
from lab.rag.chunk import chunk_records
from lab.rag.hybrid import HybridRetriever

os.environ["EMBED_BACKEND"] = "stub"  # deterministic/offline


def test_hybrid_retrieval_works():
    records = list(load_texts("lab/rag/fixtures"))
    chunks = chunk_records(records, max_chars=200)
    hr = HybridRetriever(chunks, alpha=0.5)
    res = hr.query("RAG system chunks", k=3)
    assert isinstance(res, list) and len(res) >= 1
    # ensure fields are present
    hit = res[0]
    for key in ("chunk_id", "text", "source", "score", "vector", "bm25"):
        assert key in hit
