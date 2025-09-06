from typing import List, Dict
try:
    from rank_bm25 import BM25Okapi  # lightweight dependency
except Exception as e:
    BM25Okapi = None

def _tokenize(s: str) -> List[str]:
    import re
    return [t for t in re.findall(r"[A-Za-z0-9]+", s.lower()) if t]

class BM25Retriever:
    def __init__(self, chunks: List[Dict]):
        if BM25Okapi is None:
            raise RuntimeError("rank-bm25 not installed; install it or swap retriever.")
        self.chunks = chunks
        self.corpus_tokens = [ _tokenize(c["text"]) for c in chunks ]
        self.bm25 = BM25Okapi(self.corpus_tokens)

    def query(self, q: str, k: int = 3) -> List[Dict]:
        q_tokens = _tokenize(q)
        scores = self.bm25.get_scores(q_tokens)
        top_idx = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]
        out = []
        for i in top_idx:
            c = self.chunks[i]
            out.append({
                "chunk_id": c["id"],
                "text": c["text"],
                "source": c["meta"]["source"],
                "score": float(scores[i]),
            })
        return out
