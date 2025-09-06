Version: v0.6.2

# Use Case: AI-Assisted Development

## Problem
Developers need fast, trustworthy answers grounded in repo docs, tests, and CI evidence.

## Approach
- RAG over project docs and code comments.
- Tools: `search_docs`, `run_tests`, `eval_metrics`.
- Guardrails: reviewer tool to enforce policy (PII, secrets).

## Success Metrics
- Time-to-answer p50 < 30s
- Answer grounded (cited passages) ≥ 90%
- False-positive lint/test suggestions ≤ 5%

## Minimal Flow
1. User asks a repo-specific question.
2. System retrieves top-3 passages.
3. Module synthesizes answer with citations.
4. Compliance review (pass/fail + notes).
