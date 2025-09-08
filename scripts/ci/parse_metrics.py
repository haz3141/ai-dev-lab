#!/usr/bin/env python3
"""Parse evaluation metrics and enforce gates."""

import json
import sys


def load_metrics(metrics_file: str) -> dict:
    """Load metrics from JSON file."""
    with open(metrics_file) as f:
        return json.load(f)


def check_gates(metrics: dict) -> tuple[bool, list[str]]:
    """Check if metrics pass all gates."""
    failures = []

    # Retrieval gates
    retrieval = metrics.get("retrieval", {})
    if retrieval.get("recall_at_5", 0) < 0.85:
        failures.append(f"Recall@5: {retrieval.get('recall_at_5', 0):.3f} < 0.85")
    if retrieval.get("recall_at_10", 0) < 0.92:
        failures.append(f"Recall@10: {retrieval.get('recall_at_10', 0):.3f} < 0.92")
    if retrieval.get("mrr_at_10", 0) < 0.60:
        failures.append(f"MRR@10: {retrieval.get('mrr_at_10', 0):.3f} < 0.60")

    # Answer quality gates
    answer = metrics.get("answer", {})
    if answer.get("f1", 0) < 0.55:
        failures.append(f"F1: {answer.get('f1', 0):.3f} < 0.55")

    # Judge gates
    judge = metrics.get("judge", {})
    if judge.get("pass_rate", 0) < 0.80:
        failures.append(f"Judge Pass Rate: {judge.get('pass_rate', 0):.3f} < 0.80")

    # Faithfulness gates
    faithfulness = metrics.get("faithfulness", {})
    if faithfulness.get("hallucination_rate", 1) > 0.05:
        failures.append(
            f"Hallucination Rate: {faithfulness.get('hallucination_rate', 1):.3f} > 0.05",
        )

    # Context utilization gates
    context = metrics.get("context", {})
    if context.get("utilization_rate", 0) < 0.90:
        failures.append(f"Context Utilization: {context.get('utilization_rate', 0):.3f} < 0.90")

    # Performance gates
    perf = metrics.get("perf", {})
    if perf.get("p95_s", 999) > 3.5:
        failures.append(f"P95 Latency: {perf.get('p95_s', 999):.1f}s > 3.5s")

    return len(failures) == 0, failures


def print_results(metrics: dict, *, passed: bool, failures: list[str]):
    """Print formatted results table."""
    print("\n" + "=" * 60)
    print("RAG EVALUATION GATES RESULTS")
    print("=" * 60)

    # Retrieval metrics
    retrieval = metrics.get("retrieval", {})
    print("Retrieval Metrics:")
    print(
        f"  Recall@5:  {retrieval.get('recall_at_5', 0):.3f} {'✅' if retrieval.get('recall_at_5', 0) >= 0.85 else '❌'}",
    )
    print(
        f"  Recall@10: {retrieval.get('recall_at_10', 0):.3f} {'✅' if retrieval.get('recall_at_10', 0) >= 0.92 else '❌'}",
    )
    print(
        f"  MRR@10:    {retrieval.get('mrr_at_10', 0):.3f} {'✅' if retrieval.get('mrr_at_10', 0) >= 0.60 else '❌'}",
    )

    # Answer quality
    answer = metrics.get("answer", {})
    print("\nAnswer Quality:")
    print(f"  F1:        {answer.get('f1', 0):.3f} {'✅' if answer.get('f1', 0) >= 0.55 else '❌'}")

    # Judge metrics
    judge = metrics.get("judge", {})
    print("\nJudge Metrics:")
    print(
        f"  Pass Rate: {judge.get('pass_rate', 0):.3f} {'✅' if judge.get('pass_rate', 0) >= 0.80 else '❌'}",
    )

    # Faithfulness
    faithfulness = metrics.get("faithfulness", {})
    print("\nFaithfulness:")
    print(
        f"  Hallucination: {faithfulness.get('hallucination_rate', 0):.3f} {'✅' if faithfulness.get('hallucination_rate', 1) <= 0.05 else '❌'}",
    )

    # Context utilization
    context = metrics.get("context", {})
    print("\nContext Utilization:")
    print(
        f"  Utilization:   {context.get('utilization_rate', 0):.3f} {'✅' if context.get('utilization_rate', 0) >= 0.90 else '❌'}",
    )

    # Performance
    perf = metrics.get("perf", {})
    print("\nPerformance:")
    print(
        f"  P95 Latency:   {perf.get('p95_s', 0):.1f}s {'✅' if perf.get('p95_s', 999) <= 3.5 else '❌'}",
    )

    print("=" * 60)
    if passed:
        print("🎉 ALL GATES PASSED")
    else:
        print("❌ GATES FAILED:")
        for failure in failures:
            print(f"  - {failure}")
    print("=" * 60)

    return passed


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Parse RAG evaluation metrics")
    parser.add_argument("metrics_file", help="Path to metrics.json file")
    args = parser.parse_args()

    # Load metrics
    metrics = load_metrics(args.metrics_file)

    # Check gates
    passed, failures = check_gates(metrics)

    # Print results
    print_results(metrics, passed=passed, failures=failures)

    # Exit with appropriate code
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
