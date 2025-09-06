# lab/rag/hybrid.py
from __future__ import annotations

import os
from typing import List, Dict

from lab.rag.embed import Embeddings
from lab.rag.retrieve import BM25Retriever  # re-use BM25
from lab.rag.vector import FaissIndex


def build_vector_index(chunks: List[Dict], emb: Embeddings) -> FaissIndex:
    vecs = emb.encode([c["text"] for c in chunks])
    dim = len(vecs[0]) if vecs else 128
    idx = FaissIndex(dim=dim, metric="ip")
    idx.add([c["id"] for c in chunks], vecs)
    return idx


class HybridRetriever:
    """
    alpha: weight for vector score; (1-alpha) for BM25
    (both normalized to [0,1])
    """
    def __init__(self, chunks: List[Dict], alpha: float | None = None,
                 emb: Embeddings | None = None):
        self.chunks = chunks
        self.alpha = float(alpha if alpha is not None else
                          os.getenv("HYBRID_ALPHA", "0.5"))
        self.emb = emb or Embeddings()
        # BM25
        self.bm25 = BM25Retriever(chunks)
        # Vector
        self.index = build_vector_index(chunks, self.emb)

    def query(self, q: str, k: int = 5) -> List[Dict]:
        # vector scores
        q_vec = self.emb.encode([q])[0]
        v_hits = self.index.search([q_vec], k=max(k, 10))[0]
        # fetch more for better merge
        v_map = {cid: score for cid, score in v_hits}
        # bm25 scores
        bm_hits = self.bm25.query(q, k=max(k, 10))
        bm_map = {h["chunk_id"]: h["score"] for h in bm_hits}

        # normalize scores to [0,1]
        def norm(d: Dict[str, float]) -> Dict[str, float]:
            if not d:
                return {}
            vals = list(d.values())
            lo, hi = min(vals), max(vals)
            if hi - lo <= 1e-9:
                return {k: 1.0 for k in d}
            return {k: (v - lo) / (hi - lo) for k, v in d.items()}

        v_n = norm(v_map)
        bm_n = norm(bm_map)
        all_ids = set(v_map) | set(bm_map)
        merged = []
        for cid in all_ids:
            vs = v_n.get(cid, 0.0)
            bs = bm_n.get(cid, 0.0)
            score = self.alpha * vs + (1.0 - self.alpha) * bs
            merged.append((cid, score))

        merged.sort(key=lambda x: x[1], reverse=True)
        top = merged[:k]
        # materialize
        chunk_by_id = {c["id"]: c for c in self.chunks}
        return [{
            "chunk_id": cid,
            "text": chunk_by_id[cid]["text"],
            "source": chunk_by_id[cid]["meta"]["source"],
            "score": float(score),
            "vector": float(v_map.get(cid, 0.0)),
            "bm25": float(bm_map.get(cid, 0.0)),
        } for cid, score in top]
