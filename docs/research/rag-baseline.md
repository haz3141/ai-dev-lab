<!--
Version: 0.6.4
-->
# RAG Baseline — Research Findings (v0.6.4)

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
| 2025-09-06 | `<sha>`    | 3 | 1000       | 15%     | 10        | _TBD_    | _TBD_     | Initial run with QA module |

> **Method:** `lab/rag/eval.py` with fixed seed and small eval set (10 Q/A).  
> **Repro:** `python lab/rag/eval.py --config lab/rag/config.yaml --seed 42`  
> **QA Module:** `lab/rag/qa.py` provides retrieval + synthesis with grounding  
> **Tests:** `tests/rag/test_qa_grounding.py` validates citation functionality

## QA Module Features
- **Retrieval + Synthesis**: Combines embedding retrieval with answer generation
- **Grounding**: Ensures all answers cite specific passage IDs
- **Confidence Scoring**: Provides confidence metrics based on passage relevance
- **Batch Processing**: Supports multiple questions in single evaluation
- **Deterministic**: Fixed seed ensures reproducible results

## Change Log
- v0.6.2: Created baseline log; wired to eval harness.
- v0.6.2: Added QA module with grounding support and eval harness.
