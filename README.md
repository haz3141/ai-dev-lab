<!-- Version: 0.6.0 -->
# AI Dev Lab v0.6.0

AI Development Lab with MCP Server for secure, auditable AI tool interactions.

## Quick Start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start the MCP server:
   ```bash
   uvicorn mcp_server.server:app --reload
   ```

3. Run tests:
   ```bash
   pytest
   ```

## Architecture

- **MCP Server**: FastAPI-based server providing AI tools via MCP protocol
- **Security**: Guardian-based access control and PII redaction
- **Audit**: Comprehensive logging of all tool interactions
- **Evaluation**: Automated testing and metrics for AI models

## Development

See [docs/cursor-usage.md](docs/cursor-usage.md) for Cursor IDE setup and usage.
