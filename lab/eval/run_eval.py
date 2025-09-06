"""
Evaluation Runner

Runs evaluation on retrieval systems with deterministic test harness.
"""

import json
import os
from typing import Any, Dict, List

from lab.eval.metrics import DeterministicTestHarness, RetrievalEvaluator


def load_test_dataset(dataset_path: str) -> List[Dict[str, Any]]:
    """Load test dataset from JSONL file."""
    test_cases = []

    if not os.path.exists(dataset_path):
        # Create a sample dataset if it doesn't exist
        return create_sample_dataset()

    with open(dataset_path, "r") as f:
        for line in f:
            if line.strip():
                test_cases.append(json.loads(line))

    return test_cases


def create_sample_dataset() -> List[Dict[str, Any]]:
    """Create a sample test dataset for evaluation."""
    return [
        {
            "query": "machine learning algorithms",
            "documents": [
                "Introduction to machine learning and neural networks",
                "Deep learning techniques for image recognition",
                "Statistical methods for data analysis",
                "Natural language processing with transformers",
                "Computer vision applications in healthcare",
            ],
            "relevant_docs": [
                "Introduction to machine learning and neural networks",
                "Deep learning techniques for image recognition",
            ],
        },
        {
            "query": "data visualization tools",
            "documents": [
                "Python libraries for data visualization",
                "Interactive dashboards with Plotly",
                "Statistical analysis with R",
                "Database design principles",
                "Web development with React",
            ],
            "relevant_docs": [
                "Python libraries for data visualization",
                "Interactive dashboards with Plotly",
            ],
        },
        {
            "query": "database optimization",
            "documents": [
                "SQL query optimization techniques",
                "NoSQL database design patterns",
                "Database indexing strategies",
                "Cloud computing platforms",
                "API development best practices",
            ],
            "relevant_docs": [
                "SQL query optimization techniques",
                "Database indexing strategies",
            ],
        },
    ]


def run_evaluation(dataset_path: str = "lab/eval/dataset.jsonl") -> Dict[str, Any]:
    """Run evaluation on the test dataset."""
    print("Loading test dataset...")
    test_cases = load_test_dataset(dataset_path)

    print(f"Loaded {len(test_cases)} test cases")

    # Initialize evaluator and test harness
    evaluator = RetrievalEvaluator(k_values=[1, 3, 5])
    test_harness = DeterministicTestHarness(evaluator)

    print("Running evaluation...")
    metrics = test_harness.run_evaluation(test_cases)

    # Format results
    results = {
        "dataset_size": len(test_cases),
        "metrics": {
            "hit_at_k": metrics.hit_at_k,
            "mrr_at_k": metrics.mrr_at_k,
            "precision_at_k": metrics.precision_at_k,
            "recall_at_k": metrics.recall_at_k,
            "f1_at_k": metrics.f1_at_k,
        },
    }

    return results


def print_metrics(results: Dict[str, Any]):
    """Print evaluation metrics in a formatted way."""
    print("\n" + "=" * 50)
    print("EVALUATION RESULTS")
    print("=" * 50)
    print(f"Dataset size: {results['dataset_size']} test cases")
    print()

    metrics = results["metrics"]

    print("Hit@K:")
    for k, score in metrics["hit_at_k"].items():
        print(f"  Hit@{k}: {score:.3f}")

    print("\nMRR@K:")
    for k, score in metrics["mrr_at_k"].items():
        print(f"  MRR@{k}: {score:.3f}")

    print("\nPrecision@K:")
    for k, score in metrics["precision_at_k"].items():
        print(f"  Precision@{k}: {score:.3f}")

    print("\nRecall@K:")
    for k, score in metrics["recall_at_k"].items():
        print(f"  Recall@{k}: {score:.3f}")

    print("\nF1@K:")
    for k, score in metrics["f1_at_k"].items():
        print(f"  F1@{k}: {score:.3f}")

    print("=" * 50)


def main():
    """Main evaluation runner."""
    import argparse

    parser = argparse.ArgumentParser(description="Run retrieval evaluation")
    parser.add_argument(
        "--dataset",
        default="lab/eval/dataset.jsonl",
        help="Path to test dataset JSONL file",
    )
    parser.add_argument("--output", help="Path to save results JSON file")

    args = parser.parse_args()

    # Run evaluation
    results = run_evaluation(args.dataset)

    # Print results
    print_metrics(results)

    # Save results if output path specified
    if args.output:
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to {args.output}")


if __name__ == "__main__":
    main()
