Version: v0.6.2

# MCP Tool Promotions — Evidence

## Tools promoted to app scope

- `search_docs` - Document search functionality
- `summarize` - Text summarization functionality

## CI Evidence

- `mcp-allowlist` workflow: schema validator ✅
- `pytest` allowlist tests: presence + denial ✅
- Coverage gating: 68% threshold enforced ✅

## App Structure Evidence

- `app/mcp-servers/promotions/server.py` - Production runtime server
- `app/mcp-servers/promotions/pyproject.toml` - Minimal runtime dependencies
- Lab dependencies properly abstracted

## Runtime Evidence (paste after manual check)

- Example `search_docs` invocation output…
- Example `summarize` invocation output…
- Health check endpoint response…
