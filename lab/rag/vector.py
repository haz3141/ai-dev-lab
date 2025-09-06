# lab/rag/vector.py
from __future__ import annotations

from typing import List, Tuple
import numpy as np


class FaissIndex:
    def __init__(self, dim: int, metric: str = "ip"):
        self.dim = dim
        self.metric = metric
        self.ids: List[str] = []
        try:
            import faiss  # type: ignore
            self.faiss = faiss
            if metric == "l2":
                self.index = faiss.IndexFlatL2(dim)
            else:
                self.index = faiss.IndexFlatIP(dim)
        except Exception:  # noqa: BLE001
            # Minimal numpy fallback (slow, test-only)
            self.faiss = None
            self.index = None
            self._matrix: np.ndarray | None = None

    def add(self, ids: List[str], vectors: List[List[float]]):
        mat = np.array(vectors, dtype="float32")
        if self.faiss:
            if self.metric != "l2":
                # assume vectors are normalized upstream for IP (cosine)
                pass
            self.index.add(mat)
            self.ids.extend(ids)
        else:
            self.ids.extend(ids)
            self._matrix = (mat if self._matrix is None else
                            np.vstack([self._matrix, mat]))

    def search(self, query_vecs: List[List[float]],
               k: int = 3) -> List[List[Tuple[str, float]]]:
        Q = np.array(query_vecs, dtype="float32")
        if self.faiss:
            D, indices = self.index.search(Q, k)
            out = []
            for row_d, row_i in zip(D, indices):
                out.append([
                    (self.ids[i], float(d)) for i, d in zip(row_i, row_d)
                    if i >= 0
                ])
            return out
        else:
            # brute force cosine/IP
            X = self._matrix
            out = []
            for q in Q:
                sims = (X @ q)
                idx = np.argsort(-sims)[:k]
                out.append([(self.ids[int(i)], float(sims[int(i)]))
                           for i in idx])
            return out
