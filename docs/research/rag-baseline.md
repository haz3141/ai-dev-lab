# RAG Baseline — Research Findings (v0.6.2)

**Scope:** Track chunking, retrieval, and QA metrics for the baseline system.

## Current Configuration
- Chunk size: **1000 tokens**
- Overlap: **15%**
- Retriever: **cosine** over **all-MiniLM-L6-v2**
- Top-k: **3–5**
- Temperature: **low** (for determinism in QA)

## Baseline Metrics (seeded)
| Date       | Commit SHA | k | Chunk Size | Overlap | Eval Size | Accuracy | Grounding | Notes |
|------------|------------|---|------------|---------|-----------|----------|-----------|-------|
| 2025-09-06 | `<sha>`    | 3 | 1000       | 15%     | 15        | _TBD_    | _TBD_     | Initial run |

> **Method:** `lab/rag/eval.py` with fixed seed and small eval set (10–20 Q/A).  
> **Repro:** `python lab/rag/eval.py --config lab/rag/config.yaml --seed 42`

## Change Log
- v0.6.2: Created baseline log; wired to eval harness.
