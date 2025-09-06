from lab.rag.ingest import load_texts
from lab.rag.chunk import chunk_records
from lab.rag.retrieve import BM25Retriever

def test_bm25_retrieval_minimal(tmp_path):
    # Use repo fixture
    records = list(load_texts("lab/rag/fixtures"))
    assert len(records) >= 1
    chunks = chunk_records(records, max_chars=200)
    assert len(chunks) >= 1

    r = BM25Retriever(chunks)
    res = r.query("What is RAG?", k=2)
    assert isinstance(res, list) and len(res) >= 1
    # Check that top hit mentions RAG
    assert any("RAG" in hit["text"] or "retriev" in hit["text"].lower() for hit in res)
