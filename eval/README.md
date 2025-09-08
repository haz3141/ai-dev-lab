# RAG Evaluation Framework

## Quick Start
```bash
# Run evaluation
python eval/run.py

# Check gates
python scripts/ci/parse_metrics.py eval/runs/*/metrics.json
```

## MCP Integration

The evaluation framework is fully integrated with the MCP server, providing programmatic access to evaluation tools:

### Available MCP Tools
- **`run_eval`**: Execute RAG evaluation with custom parameters
- **`check_gates`**: Verify if evaluation gates pass based on metrics

### Usage via MCP Server
```bash
# Start MCP server
python -m uvicorn mcp_server.server:app --host 0.0.0.0 --port 8000

# Run evaluation via MCP
curl -X POST http://localhost:8000/tools/run_eval \
  -H "Content-Type: application/json" \
  -d '{
    "dataset": "eval/data/lab/lab_dev.jsonl",
    "output_dir": "eval/runs/mcp-test",
    "timeout": 300
  }'

# Check gates via MCP
curl -X POST http://localhost:8000/tools/check_gates \
  -H "Content-Type: application/json" \
  -d '{"metrics_file": "eval/runs/mcp-test/metrics.json"}'
```

### Programmatic Usage
```python
from mcp_server.tools.terminal_helper import run_eval_safe, check_gates_safe

# Run evaluation
result = run_eval_safe(
    dataset="eval/data/lab/lab_dev.jsonl",
    output_dir="eval/runs/programmatic",
    timeout=300
)

# Check gates
gates_result = check_gates_safe("eval/runs/programmatic/metrics.json")
```

## Configuration
- `eval/configs/lab.yaml` - Evaluation configuration
- `eval/data/lab/` - Test datasets

## Gates
- Retrieval: Recall@5 ≥ 0.85, Recall@10 ≥ 0.92, MRR@10 ≥ 0.60
- Answer Quality: F1 ≥ 0.55
- Judge: Pass Rate ≥ 0.80
- Faithfulness: Hallucination Rate ≤ 0.05
- Context: Utilization Rate ≥ 0.90
- Performance: P95 ≤ 3.5s

## CI Integration

The evaluation framework includes GitHub Actions workflow for automated testing:

- **File**: `.github/workflows/rag-gates.yml`
- **Triggers**: Push to main/develop branches, pull requests
- **Tests**: MCP server, evaluation pipeline, gate validation
- **Artifacts**: Test results and metrics uploaded

## Security

All evaluation tools are protected by the security guardian:
- Access control via MCP allowlist
- Audit logging of all operations
- Safe execution with timeouts and limits
