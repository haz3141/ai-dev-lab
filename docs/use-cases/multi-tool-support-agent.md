# Use Case: Multi-Tool Support Agent

## Problem
Operators need a single surface to triage issues across logs, tests, and docs.

## Approach
- Tools: `audit_recent`, `audit_by_tool`, `search_docs`, optional external API calls.
- Summarize + cite; escalate when confidence low.

## Success Metrics
- Mean time to detect regression (MTTD) ↓ 30%
- Escalation accuracy ≥ 85%
- Coverage of top-10 frequent issues ≥ 90%

## Minimal Flow
1. Operator triggers triage command.
2. Agent fetches recent CI/audit signals.
3. Agent summarizes probable cause with citations.
4. Operator approves or asks follow-ups.
