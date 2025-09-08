# mcp_server/tools/summarize.py
import json
from pathlib import Path


def register(app):
    @app.tool()
    def summarize(text: str, max_sentences: int = 3) -> dict:
        """Deterministic extractive summary (no model dependency)."""
        if not text:
            return {"summary": ""}

        parts = [s.strip() for s in text.replace("\n", " ").split(".") if s.strip()]
        keep = parts[: max(1, int(max_sentences))]
        summary = ". ".join(keep)
        if text.strip().endswith("."):
            summary += "."
        return {"summary": summary}

    @app.tool()
    def summarize_eval(run_dir: str) -> dict:
        """Summarize evaluation results from a run directory."""
        try:
            metrics_file = Path(run_dir) / "metrics.json"
            if not metrics_file.exists():
                return {"status": "error", "message": "No metrics.json found"}

            with open(metrics_file) as f:
                metrics = json.load(f)

            # Extract key metrics
            retrieval = metrics.get("retrieval", {})
            answer = metrics.get("answer", {})
            judge = metrics.get("judge", {})
            faithfulness = metrics.get("faithfulness", {})
            context = metrics.get("context", {})
            perf = metrics.get("perf", {})

            # Determine pass/fail status
            passed = (
                retrieval.get("recall_at_5", 0) >= 0.85
                and retrieval.get("recall_at_10", 0) >= 0.92
                and retrieval.get("mrr_at_10", 0) >= 0.60
                and answer.get("f1", 0) >= 0.55
                and judge.get("pass_rate", 0) >= 0.80
                and faithfulness.get("hallucination_rate", 1) <= 0.05
                and context.get("utilization_rate", 0) >= 0.90
                and perf.get("p95_s", 999) <= 3.5
            )

            status = "PASS" if passed else "FAIL"

            summary = f"RAG Gates {status}: R@5={retrieval.get('recall_at_5', 0):.2f}, R@10={retrieval.get('recall_at_10', 0):.2f}, MRR@10={retrieval.get('mrr_at_10', 0):.2f}, F1={answer.get('f1', 0):.2f}, Judge={judge.get('pass_rate', 0):.2f}, Halluc={faithfulness.get('hallucination_rate', 0):.2f}, Context={context.get('utilization_rate', 0):.2f}, P95={perf.get('p95_s', 0):.1f}s"

            return {
                "status": status,
                "summary": summary,
                "metrics": {
                    "retrieval": retrieval,
                    "answer": answer,
                    "judge": judge,
                    "faithfulness": faithfulness,
                    "context": context,
                    "perf": perf,
                },
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
