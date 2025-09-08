<!-- Version: 0.6.4 -->
# AI-Enhanced Dev Lab v0.6.4

AI Development Lab with MCP Server for secure, auditable AI tool interactions and RAG evaluation gates.

## Quick Start

### Two Entrypoints

This project supports two distinct MCP server entrypoints for different use cases:

#### 1. Cursor IDE Integration (Stdio Transport)
For local development and Cursor IDE integration:
```bash
# Install dependencies
pip install -r requirements.txt

# Start MCP server for Cursor (stdio transport)
python -m mcp_server.simple_server
```

**Cursor Configuration**: The `.cursor/mcp.json` file is pre-configured to connect to this stdio server for AI-assisted development.

#### 2. Production HTTP Server (Docker)
For production deployment and HTTP-based tool access:
```bash
# Build and run with Docker
docker build -t lab-mcp-server .
docker run -p 8765:8765 lab-mcp-server

# Or use docker-compose
docker-compose up
```

**HTTP Endpoints**: The server exposes REST endpoints at `http://localhost:8765` for programmatic tool access.

### Testing
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

# Start MCP server (stdio for Cursor, or HTTP server for programmatic access)
python -m mcp_server.simple_server  # For Cursor IDE
# OR
docker-compose up                    # For HTTP API access
```

### MCP Tools Available

The MCP server provides the following tools:

#### Terminal Operations
- **`run_command`**: Execute terminal commands safely with timeout
- **`check_file`**: Check if files exist and get metadata
- **`read_file`**: Safely read files with line limits
- **`list_directory`**: List directory contents with limits

#### Evaluation Operations
- **`run_eval`**: Run RAG evaluation safely
- **`check_gates`**: Check if evaluation gates pass

#### Usage Examples
```bash
# Test MCP server
curl -X POST http://localhost:8000/tools/run_command \
  -H "Content-Type: application/json" \
  -d '{"command": "ls -la", "timeout": 10}'

# Check file existence
curl -X POST http://localhost:8000/tools/check_file \
  -H "Content-Type: application/json" \
  -d '{"filepath": "eval/run.py"}'

# Run evaluation
curl -X POST http://localhost:8000/tools/run_eval \
  -H "Content-Type: application/json" \
  -d '{"dataset": "eval/data/lab/lab_dev.jsonl", "output_dir": "eval/runs/test"}'
```

## Architecture

- **MCP Server**: FastAPI-based server with dual transport support (stdio for Cursor IDE, HTTP for programmatic access)
- **Security**: Guardian-based access control and PII redaction
- **Audit**: Comprehensive logging of all tool interactions
- **Evaluation**: Automated testing and metrics for AI models
- **RAG Gates**: Comprehensive evaluation framework with automated CI integration
- **Dual Entrypoints**: Clean separation between development (Cursor stdio) and production (Docker HTTP)

## Project Structure
- `lab/` - Research and development experiments
- `eval/` - Evaluation framework and gates
- `mcp_server/` - MCP server implementation
- `evidence/` - Evaluation evidence and reports

## Development

See [docs/cursor-usage.md](docs/cursor-usage.md) for Cursor IDE setup and usage.
