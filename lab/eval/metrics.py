"""Evaluation Metrics for Retrieval Systems

Provides hit@k, MRR@k, and other retrieval evaluation metrics.
"""

from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass
class RetrievalResult:
    """Represents a single retrieval result."""

    query: str
    retrieved_docs: list[str]
    relevant_docs: list[str]
    scores: list[float] | None = None


@dataclass
class EvaluationMetrics:
    """Container for evaluation metrics."""

    hit_at_k: dict[int, float]
    mrr_at_k: dict[int, float]
    precision_at_k: dict[int, float]
    recall_at_k: dict[int, float]
    f1_at_k: dict[int, float]


class RetrievalEvaluator:
    """Evaluator for retrieval systems with deterministic testing capabilities."""

    def __init__(self, k_values: list[int] = None):
        self.k_values = k_values or [1, 3, 5, 10]
        self.results: list[RetrievalResult] = []

    def add_result(
        self,
        query: str,
        retrieved_docs: list[str],
        relevant_docs: list[str],
        scores: list[float] | None = None,
    ):
        """Add a retrieval result for evaluation."""
        result = RetrievalResult(
            query=query,
            retrieved_docs=retrieved_docs,
            relevant_docs=relevant_docs,
            scores=scores,
        )
        self.results.append(result)

    def hit_at_k(self, k: int) -> float:
        """Calculate Hit@K metric."""
        if not self.results:
            return 0.0

        hits = 0
        for result in self.results:
            top_k = result.retrieved_docs[:k]
            if any(doc in result.relevant_docs for doc in top_k):
                hits += 1

        return hits / len(self.results)

    def mrr_at_k(self, k: int) -> float:
        """Calculate MRR@K (Mean Reciprocal Rank) metric."""
        if not self.results:
            return 0.0

        reciprocal_ranks = []
        for result in self.results:
            top_k = result.retrieved_docs[:k]
            for i, doc in enumerate(top_k):
                if doc in result.relevant_docs:
                    reciprocal_ranks.append(1.0 / (i + 1))
                    break
            else:
                reciprocal_ranks.append(0.0)

        return np.mean(reciprocal_ranks)

    def precision_at_k(self, k: int) -> float:
        """Calculate Precision@K metric."""
        if not self.results:
            return 0.0

        precisions = []
        for result in self.results:
            top_k = result.retrieved_docs[:k]
            relevant_retrieved = sum(1 for doc in top_k if doc in result.relevant_docs)
            precision = relevant_retrieved / min(k, len(top_k)) if top_k else 0.0
            precisions.append(precision)

        return np.mean(precisions)

    def recall_at_k(self, k: int) -> float:
        """Calculate Recall@K metric."""
        if not self.results:
            return 0.0

        recalls = []
        for result in self.results:
            top_k = result.retrieved_docs[:k]
            relevant_retrieved = sum(1 for doc in top_k if doc in result.relevant_docs)
            recall = relevant_retrieved / len(result.relevant_docs) if result.relevant_docs else 0.0
            recalls.append(recall)

        return np.mean(recalls)

    def f1_at_k(self, k: int) -> float:
        """Calculate F1@K metric."""
        precision = self.precision_at_k(k)
        recall = self.recall_at_k(k)

        if precision + recall == 0:
            return 0.0

        return 2 * (precision * recall) / (precision + recall)

    def evaluate_all(self) -> EvaluationMetrics:
        """Calculate all metrics for all k values."""
        metrics = EvaluationMetrics(
            hit_at_k={},
            mrr_at_k={},
            precision_at_k={},
            recall_at_k={},
            f1_at_k={},
        )

        for k in self.k_values:
            metrics.hit_at_k[k] = self.hit_at_k(k)
            metrics.mrr_at_k[k] = self.mrr_at_k(k)
            metrics.precision_at_k[k] = self.precision_at_k(k)
            metrics.recall_at_k[k] = self.recall_at_k(k)
            metrics.f1_at_k[k] = self.f1_at_k(k)

        return metrics

    def clear_results(self):
        """Clear all stored results."""
        self.results = []


class DeterministicTestHarness:
    """Deterministic test harness using stub embeddings for reproducible evaluation."""

    def __init__(self, evaluator: RetrievalEvaluator = None):
        self.evaluator = evaluator or RetrievalEvaluator()
        self.stub_embeddings = {}

    def create_stub_embedding(self, text: str) -> list[float]:
        """Create a deterministic stub embedding for text."""
        # Simple hash-based embedding for deterministic results
        import hashlib

        hash_obj = hashlib.md5(text.encode())
        hash_bytes = hash_obj.digest()

        # Convert to 128-dimensional vector
        embedding = []
        for i in range(0, len(hash_bytes), 4):
            chunk = hash_bytes[i : i + 4]
            if len(chunk) == 4:
                value = int.from_bytes(chunk, byteorder="big")
                # Normalize to [-1, 1] range
                normalized = (value / (2**32 - 1)) * 2 - 1
                embedding.append(normalized)

        # Pad or truncate to exactly 128 dimensions
        while len(embedding) < 128:
            embedding.append(0.0)
        embedding = embedding[:128]

        return embedding

    def cosine_similarity(self, a: list[float], b: list[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        dot_product = sum(x * y for x, y in zip(a, b, strict=False))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot_product / (norm_a * norm_b)

    def retrieve_documents(self, query: str, documents: list[str], k: int = 5) -> list[str]:
        """Retrieve top-k documents using stub embeddings."""
        query_embedding = self.create_stub_embedding(query)

        similarities = []
        for doc in documents:
            doc_embedding = self.create_stub_embedding(doc)
            similarity = self.cosine_similarity(query_embedding, doc_embedding)
            similarities.append((similarity, doc))

        # Sort by similarity (descending) and return top-k
        similarities.sort(key=lambda x: x[0], reverse=True)
        return [doc for _, doc in similarities[:k]]

    def run_evaluation(self, test_cases: list[dict[str, Any]]) -> EvaluationMetrics:
        """Run evaluation on test cases using deterministic retrieval."""
        self.evaluator.clear_results()

        for case in test_cases:
            query = case["query"]
            documents = case["documents"]
            relevant_docs = case["relevant_docs"]
            k = case.get("k", 5)

            retrieved_docs = self.retrieve_documents(query, documents, k)
            self.evaluator.add_result(query, retrieved_docs, relevant_docs)

        return self.evaluator.evaluate_all()


# Global evaluator instance
evaluator = RetrievalEvaluator()
test_harness = DeterministicTestHarness(evaluator)
