Version: v0.6.2

"""
RAG Evaluation Harness - Run evaluations with fixed seed for reproducibility.

This module provides a simple evaluation framework for testing RAG performance
with a small, fixed dataset to ensure deterministic results.
"""

import logging
import json
import random
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

from .qa import QAModule, QAResult

logger = logging.getLogger(__name__)


@dataclass
class EvalQuestion:
    """Evaluation question with expected answer."""
    question: str
    expected_answer: str
    context: Optional[str] = None
    difficulty: str = "medium"
    category: str = "general"


@dataclass
class EvalResult:
    """Result of a single evaluation question."""
    question: str
    predicted_answer: str
    expected_answer: str
    confidence: float
    passage_ids: List[str]
    is_grounded: bool
    is_correct: bool
    metadata: Dict[str, Any]


@dataclass
class EvalMetrics:
    """Aggregated evaluation metrics."""
    total_questions: int
    correct_answers: int
    grounded_answers: int
    accuracy: float
    grounding_rate: float
    avg_confidence: float
    avg_passages_per_answer: float
    results: List[EvalResult]


class RAGEvaluator:
    """RAG evaluation harness with fixed seed for reproducibility."""
    
    def __init__(self, qa_module: QAModule, seed: int = 42):
        """Initialize evaluator with QA module and fixed seed."""
        self.qa_module = qa_module
        self.seed = seed
        random.seed(seed)
        
    def create_test_dataset(self) -> List[EvalQuestion]:
        """Create a small test dataset for evaluation."""
        return [
            EvalQuestion(
                question="What is the main purpose of this AI development lab?",
                expected_answer="AI development lab for building and testing AI tools",
                difficulty="easy",
                category="project_overview"
            ),
            EvalQuestion(
                question="How does the MCP server work?",
                expected_answer="MCP server provides tool endpoints for document search and summarization",
                difficulty="medium",
                category="architecture"
            ),
            EvalQuestion(
                question="What testing framework is used?",
                expected_answer="pytest with coverage gating",
                difficulty="easy",
                category="testing"
            ),
            EvalQuestion(
                question="What is the RAG baseline configuration?",
                expected_answer="1000 token chunks, 15% overlap, cosine similarity retrieval",
                difficulty="hard",
                category="rag_config"
            ),
            EvalQuestion(
                question="How are documents ingested for RAG?",
                expected_answer="Documents are chunked and embedded using sentence transformers",
                difficulty="medium",
                category="rag_ingestion"
            ),
            EvalQuestion(
                question="What tools are promoted to app scope?",
                expected_answer="search_docs and summarize tools",
                difficulty="easy",
                category="mcp_tools"
            ),
            EvalQuestion(
                question="What is the coverage threshold?",
                expected_answer="68% coverage threshold",
                difficulty="easy",
                category="testing"
            ),
            EvalQuestion(
                question="How is linting configured?",
                expected_answer="Ruff with comprehensive rules",
                difficulty="medium",
                category="development"
            ),
            EvalQuestion(
                question="What version is currently tagged?",
                expected_answer="v0.6.2",
                difficulty="easy",
                category="versioning"
            ),
            EvalQuestion(
                question="What are the main use cases documented?",
                expected_answer="Multi-tool support agent and AI-assisted development",
                difficulty="medium",
                category="documentation"
            )
        ]
    
    def evaluate_question(self, question: EvalQuestion) -> EvalResult:
        """Evaluate a single question."""
        logger.info(f"Evaluating: {question.question[:50]}...")
        
        # Get QA result
        qa_result = self.qa_module.query(
            question.question,
            top_k=3,
            temperature=0.1  # Low temperature for deterministic output
        )
        
        # Check grounding (has passage IDs)
        is_grounded = len(qa_result.passage_ids) > 0
        
        # Simple correctness check (in production, use more sophisticated matching)
        predicted_lower = qa_result.answer.lower()
        expected_lower = question.expected_answer.lower()
        
        # Check if key terms from expected answer are present
        expected_terms = set(expected_lower.split())
        predicted_terms = set(predicted_lower.split())
        overlap = len(expected_terms.intersection(predicted_terms))
        is_correct = overlap >= len(expected_terms) * 0.3  # 30% overlap threshold
        
        return EvalResult(
            question=question.question,
            predicted_answer=qa_result.answer,
            expected_answer=question.expected_answer,
            confidence=qa_result.confidence,
            passage_ids=qa_result.passage_ids,
            is_grounded=is_grounded,
            is_correct=is_correct,
            metadata={
                "difficulty": question.difficulty,
                "category": question.category,
                "num_passages": len(qa_result.passages)
            }
        )
    
    def run_evaluation(self, questions: Optional[List[EvalQuestion]] = None) -> EvalMetrics:
        """Run full evaluation on test dataset."""
        if questions is None:
            questions = self.create_test_dataset()
        
        logger.info(f"Running evaluation on {len(questions)} questions with seed {self.seed}")
        
        results = []
        for question in questions:
            result = self.evaluate_question(question)
            results.append(result)
        
        # Calculate metrics
        total_questions = len(results)
        correct_answers = sum(1 for r in results if r.is_correct)
        grounded_answers = sum(1 for r in results if r.is_grounded)
        avg_confidence = sum(r.confidence for r in results) / total_questions
        avg_passages = sum(len(r.passage_ids) for r in results) / total_questions
        
        metrics = EvalMetrics(
            total_questions=total_questions,
            correct_answers=correct_answers,
            grounded_answers=grounded_answers,
            accuracy=correct_answers / total_questions,
            grounding_rate=grounded_answers / total_questions,
            avg_confidence=avg_confidence,
            avg_passages_per_answer=avg_passages,
            results=results
        )
        
        logger.info(f"Evaluation complete: {metrics.accuracy:.2%} accuracy, {metrics.grounding_rate:.2%} grounding")
        return metrics
    
    def save_results(self, metrics: EvalMetrics, output_path: str):
        """Save evaluation results to JSON file."""
        output_data = {
            "seed": self.seed,
            "timestamp": str(Path().cwd()),
            "metrics": asdict(metrics)
        }
        
        with open(output_path, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        logger.info(f"Results saved to {output_path}")


def run_eval(config_path: str = "lab/rag/config.yaml", 
             output_path: str = "eval_results.json",
             seed: int = 42) -> EvalMetrics:
    """Run evaluation with given configuration."""
    from .qa import create_qa_module
    
    # Create QA module
    qa_module = create_qa_module(config_path)
    
    # Create evaluator
    evaluator = RAGEvaluator(qa_module, seed=seed)
    
    # Run evaluation
    metrics = evaluator.run_evaluation()
    
    # Save results
    evaluator.save_results(metrics, output_path)
    
    return metrics


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run RAG evaluation")
    parser.add_argument("--config", default="lab/rag/config.yaml", help="Config file path")
    parser.add_argument("--output", default="eval_results.json", help="Output file path")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    
    args = parser.parse_args()
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Run evaluation
    metrics = run_eval(args.config, args.output, args.seed)
    
    # Print summary
    print(f"\n=== RAG Evaluation Results ===")
    print(f"Accuracy: {metrics.accuracy:.2%}")
    print(f"Grounding Rate: {metrics.grounding_rate:.2%}")
    print(f"Average Confidence: {metrics.avg_confidence:.2f}")
    print(f"Average Passages per Answer: {metrics.avg_passages_per_answer:.1f}")
    print(f"Results saved to: {args.output}")
