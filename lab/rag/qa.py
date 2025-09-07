"""QA Module - Compose retrieval + answer synthesis with citation support.

This module provides the core QA functionality that combines retrieval
with answer generation, ensuring proper grounding through passage citations.
"""

import logging
from dataclasses import dataclass
from typing import Any

from .embeddings import EmbeddingRetriever
from .ingest import DocumentStore

logger = logging.getLogger(__name__)


@dataclass
class QAResult:
    """Result of a QA query with grounding information."""

    question: str
    answer: str
    passages: list[dict[str, Any]]
    passage_ids: list[str]
    confidence: float
    metadata: dict[str, Any]


class QAModule:
    """QA module that composes retrieval with answer synthesis."""

    def __init__(self, retriever: EmbeddingRetriever, document_store: DocumentStore):
        """Initialize QA module with retriever and document store."""
        self.retriever = retriever
        self.document_store = document_store

    def query(self, question: str, top_k: int = 3, temperature: float = 0.1) -> QAResult:
        """Answer a question using retrieval + synthesis.

        Args:
            question: The question to answer
            top_k: Number of passages to retrieve
            temperature: LLM temperature for deterministic output

        Returns:
            QAResult with answer, passages, and grounding info
        """
        logger.info(f"Processing QA query: {question[:100]}...")

        # Retrieve relevant passages
        passages = self.retriever.retrieve(question, top_k=top_k)

        if not passages:
            return QAResult(
                question=question,
                answer="I couldn't find relevant information to answer this question.",
                passages=[],
                passage_ids=[],
                confidence=0.0,
                metadata={"error": "no_passages_found"},
            )

        # Extract passage IDs for grounding
        passage_ids = [p.get("id", f"passage_{i}") for i, p in enumerate(passages)]

        # Generate answer with citations
        answer = self._synthesize_answer(question, passages, temperature)

        # Calculate confidence based on passage relevance
        confidence = self._calculate_confidence(passages)

        return QAResult(
            question=question,
            answer=answer,
            passages=passages,
            passage_ids=passage_ids,
            confidence=confidence,
            metadata={"top_k": top_k, "temperature": temperature, "num_passages": len(passages)},
        )

    def _synthesize_answer(self, question: str, passages: list[dict], temperature: float) -> str:
        """Synthesize answer from retrieved passages."""
        # For now, implement a simple template-based approach
        # In production, this would use an LLM with proper prompting

        if not passages:
            return "No relevant information found."

        # Simple template-based synthesis
        context = "\n\n".join(
            [f"[Passage {i+1}]: {p.get('content', '')[:200]}..." for i, p in enumerate(passages)],
        )

        # Basic template response (replace with LLM in production)
        answer = f"""Based on the retrieved information:

{context}

Answer: This is a template-based response. In production, this would use an LLM to synthesize a proper answer to: {question}

[Cited passages: {', '.join([f"Passage {i+1}" for i in range(len(passages))])}]"""

        return answer

    def _calculate_confidence(self, passages: list[dict]) -> float:
        """Calculate confidence score based on passage relevance."""
        if not passages:
            return 0.0

        # Simple confidence based on number of passages and average score
        avg_score = sum(p.get("score", 0.0) for p in passages) / len(passages)
        passage_factor = min(len(passages) / 3.0, 1.0)  # Normalize by expected top_k

        return min(avg_score * passage_factor, 1.0)

    def batch_query(self, questions: list[str], **kwargs) -> list[QAResult]:
        """Process multiple questions in batch."""
        return [self.query(q, **kwargs) for q in questions]


def create_qa_module(config_path: str = "lab/rag/config.yaml") -> QAModule:
    """Factory function to create QA module from config."""
    import yaml

    from .embeddings import create_retriever
    from .ingest import create_document_store

    with open(config_path) as f:
        config = yaml.safe_load(f)

    retriever = create_retriever(config)
    document_store = create_document_store(config)

    return QAModule(retriever, document_store)


if __name__ == "__main__":
    # Example usage
    qa = create_qa_module()

    # Test query
    result = qa.query("What is the main purpose of this project?")
    print(f"Question: {result.question}")
    print(f"Answer: {result.answer}")
    print(f"Confidence: {result.confidence:.2f}")
    print(f"Passage IDs: {result.passage_ids}")
