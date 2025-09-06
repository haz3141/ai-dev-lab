from __future__ import annotations
import json, os
from lab.rag.ingest import load_texts
from lab.rag.chunk import chunk_records
from lab.rag.hybrid import HybridRetriever
from lab.eval.metrics import hit_at_k, mrr_at_k

os.environ.setdefault("EMBED_BACKEND", "stub")

def main(k: int = 5):
    """
    Run retrieval evaluation on the dataset.
    
    Args:
        k: Number of top results to consider for metrics
    """
    records = list(load_texts("lab/rag/fixtures"))
    chunks = chunk_records(records, max_chars=200)
    hr = HybridRetriever(chunks, alpha=0.5)

    preds, gold = [], []
    with open("lab/eval/dataset.jsonl") as f:
        for line in f:
            ex = json.loads(line)
            res = hr.query(ex["q"], k=k)
            preds.append([h["chunk_id"] for h in res])
            gold.append(ex["gold_chunk_id"])

    print(json.dumps({
        "k": k,
        "hit@k": hit_at_k(preds, gold, k),
        "mrr@k": mrr_at_k(preds, gold, k),
        "n": len(gold)
    }, indent=2))

if __name__ == "__main__":
    main()
