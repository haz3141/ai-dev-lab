Version: v0.6.2

"""
Test QA grounding functionality.

This module tests that QA responses are properly grounded with passage citations.
"""

import pytest
from unittest.mock import Mock, patch
from lab.rag.qa import QAModule, QAResult
from lab.rag.eval import RAGEvaluator, EvalQuestion, EvalResult


class TestQAGrounding:
    """Test QA grounding and citation functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_retriever = Mock()
        self.mock_document_store = Mock()
        self.qa_module = QAModule(self.mock_retriever, self.mock_document_store)
    
    def test_qa_result_has_passage_ids(self):
        """Test that QA results include passage IDs for grounding."""
        # Mock retrieval results
        mock_passages = [
            {"id": "passage_1", "content": "Test content 1", "score": 0.9},
            {"id": "passage_2", "content": "Test content 2", "score": 0.8}
        ]
        self.mock_retriever.retrieve.return_value = mock_passages
        
        # Test query
        result = self.qa_module.query("test question")
        
        # Assert grounding information is present
        assert isinstance(result, QAResult)
        assert len(result.passage_ids) == 2
        assert "passage_1" in result.passage_ids
        assert "passage_2" in result.passage_ids
        assert result.confidence > 0
        assert len(result.passages) == 2
    
    def test_qa_result_without_passages(self):
        """Test QA result when no passages are retrieved."""
        self.mock_retriever.retrieve.return_value = []
        
        result = self.qa_module.query("test question")
        
        assert isinstance(result, QAResult)
        assert len(result.passage_ids) == 0
        assert result.confidence == 0.0
        assert "couldn't find relevant information" in result.answer
    
    def test_qa_result_metadata(self):
        """Test that QA result includes proper metadata."""
        mock_passages = [
            {"id": "passage_1", "content": "Test content", "score": 0.9}
        ]
        self.mock_retriever.retrieve.return_value = mock_passages
        
        result = self.qa_module.query("test question", top_k=5, temperature=0.2)
        
        assert "top_k" in result.metadata
        assert "temperature" in result.metadata
        assert "num_passages" in result.metadata
        assert result.metadata["top_k"] == 5
        assert result.metadata["temperature"] == 0.2
        assert result.metadata["num_passages"] == 1
    
    def test_eval_result_grounding_check(self):
        """Test that evaluation properly checks for grounding."""
        # Create test question
        question = EvalQuestion(
            question="What is the test?",
            expected_answer="This is a test"
        )
        
        # Mock QA module
        mock_qa_module = Mock()
        mock_qa_module.query.return_value = QAResult(
            question="What is the test?",
            answer="This is a test based on retrieved information",
            passages=[{"id": "passage_1", "content": "test content"}],
            passage_ids=["passage_1"],
            confidence=0.8,
            metadata={}
        )
        
        # Create evaluator
        evaluator = RAGEvaluator(mock_qa_module, seed=42)
        
        # Test evaluation
        result = evaluator.evaluate_question(question)
        
        assert isinstance(result, EvalResult)
        assert result.is_grounded is True
        assert len(result.passage_ids) > 0
        assert result.confidence > 0
    
    def test_eval_result_ungrounded(self):
        """Test evaluation result when answer is not grounded."""
        question = EvalQuestion(
            question="What is the test?",
            expected_answer="This is a test"
        )
        
        # Mock QA module returning ungrounded result
        mock_qa_module = Mock()
        mock_qa_module.query.return_value = QAResult(
            question="What is the test?",
            answer="I don't know",
            passages=[],
            passage_ids=[],
            confidence=0.0,
            metadata={}
        )
        
        evaluator = RAGEvaluator(mock_qa_module, seed=42)
        result = evaluator.evaluate_question(question)
        
        assert result.is_grounded is False
        assert len(result.passage_ids) == 0
        assert result.confidence == 0.0
    
    def test_eval_metrics_grounding_rate(self):
        """Test that evaluation metrics include grounding rate."""
        # Create test questions
        questions = [
            EvalQuestion(question="Q1", expected_answer="A1"),
            EvalQuestion(question="Q2", expected_answer="A2")
        ]
        
        # Mock QA module
        mock_qa_module = Mock()
        mock_qa_module.query.side_effect = [
            QAResult("Q1", "A1", [{"id": "p1"}], ["p1"], 0.8, {}),  # Grounded
            QAResult("Q2", "A2", [], [], 0.0, {})  # Not grounded
        ]
        
        evaluator = RAGEvaluator(mock_qa_module, seed=42)
        metrics = evaluator.run_evaluation(questions)
        
        assert metrics.total_questions == 2
        assert metrics.grounded_answers == 1
        assert metrics.grounding_rate == 0.5
        assert metrics.avg_passages_per_answer == 0.5  # (1 + 0) / 2
    
    def test_deterministic_evaluation(self):
        """Test that evaluation is deterministic with fixed seed."""
        questions = [EvalQuestion(question="Q1", expected_answer="A1")]
        
        # Mock QA module with deterministic behavior
        mock_qa_module = Mock()
        mock_qa_module.query.return_value = QAResult(
            "Q1", "A1", [{"id": "p1"}], ["p1"], 0.8, {}
        )
        
        # Run evaluation twice with same seed
        evaluator1 = RAGEvaluator(mock_qa_module, seed=42)
        evaluator2 = RAGEvaluator(mock_qa_module, seed=42)
        
        metrics1 = evaluator1.run_evaluation(questions)
        metrics2 = evaluator2.run_evaluation(questions)
        
        # Results should be identical
        assert metrics1.accuracy == metrics2.accuracy
        assert metrics1.grounding_rate == metrics2.grounding_rate
        assert metrics1.avg_confidence == metrics2.avg_confidence


if __name__ == "__main__":
    pytest.main([__file__])
