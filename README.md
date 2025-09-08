<!-- Version: 0.6.4 -->
# AI-Enhanced Dev Lab v0.6.4

AI Development Lab with MCP Server for secure, auditable AI tool interactions and RAG evaluation gates.

## Quick Start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start the MCP server:
   ```bash
   .venv/bin/python -m mcp_server.simple_server
   ```

3. Run tests:
   ```bash
   pytest
   ```

## RAG Evaluation Gates

Run evaluation locally:
```bash
# Run full evaluation
python eval/run.py --dataset eval/data/lab/lab_dev.jsonl --output eval/runs/$(date +%Y%m%d-%H%M%S)

# Check gates
python scripts/ci/parse_metrics.py eval/runs/*/metrics.json

# Start MCP server
.venv/bin/python -m mcp_server.simple_server
```

## Architecture

- **MCP Server**: FastAPI-based server providing AI tools via MCP protocol
- **Security**: Guardian-based access control and PII redaction
- **Audit**: Comprehensive logging of all tool interactions
- **Evaluation**: Automated testing and metrics for AI models
- **RAG Gates**: Comprehensive evaluation framework with automated CI integration

## Project Structure
- `lab/` - Research and development experiments
- `eval/` - Evaluation framework and gates
- `mcp_server/` - MCP server implementation
- `evidence/` - Evaluation evidence and reports

## Development

See [docs/cursor-usage.md](docs/cursor-usage.md) for Cursor IDE setup and usage.
