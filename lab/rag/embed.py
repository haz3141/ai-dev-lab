# lab/rag/embed.py
from __future__ import annotations

import os
from typing import List


class Embeddings:
    """
    Simple embedding wrapper with two backends:
      - sentence-transformers (default)
      - stub (hash-based) for offline/tests: set EMBED_BACKEND=stub
    Configure model via EMBED_MODEL (e.g., all-MiniLM-L6-v2).
    """
    def __init__(self, model_name: str | None = None,
                 backend: str | None = None):
        self.backend = (backend or os.getenv("EMBED_BACKEND") or "st").lower()
        self.model_name = (model_name or os.getenv("EMBED_MODEL") or
                          "all-MiniLM-L6-v2")
        self._model = None

        if self.backend in ("stub", "fake"):
            return

        try:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
            self.dim = len(self._model.encode(["dim_probe"])[0])
        except Exception:  # noqa: BLE001
            # Fallback to stub if model unavailable
            # (keeps tests deterministic/offline)
            self.backend = "stub"
            self._model = None
            self.dim = 128

    def encode(self, texts: List[str]) -> List[List[float]]:
        if self.backend in ("stub", "fake"):
            return [self._stub(t) for t in texts]
        vecs = self._model.encode(texts, normalize_embeddings=True,
                                  show_progress_bar=False)
        return [v.tolist() for v in vecs]

    @staticmethod
    def _stub(text: str, dim: int = 128) -> List[float]:
        # Fast, deterministic hashing to unit-length-ish vector for tests
        import hashlib
        import math
        h = hashlib.sha256(text.encode("utf-8")).digest()
        # expand bytes to dim floats
        vals = [(h[i % len(h)] / 255.0) for i in range(dim)]
        # l2 normalize
        norm = math.sqrt(sum(v*v for v in vals)) or 1.0
        return [v / norm for v in vals]
