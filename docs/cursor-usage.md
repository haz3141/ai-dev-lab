<!-- Version: 0.6.0 -->
# Cursor IDE Usage Guide

This guide explains how to use Cursor IDE effectively with the AI Dev Lab project.

## Setup

### 1. Cursor Configuration

The project includes pre-configured Cursor settings in `.cursor/`:

- **Settings** (`.cursor/settings.json`): Model configuration and context settings
- **Environment** (`.cursor/environment.json`): Available commands and environment variables
- **MCP Tools** (`.cursor/mcp.json`): Allowed MCP server tools
- **Rules** (`.cursor/rules/project-guardrails.mdc`): Project-specific guardrails
- **Ignore** (`.cursorignore`): Files to exclude from indexing

### 2. MCP Server

Start the MCP server to enable tool access:

```bash
# Using Cursor command palette: Cmd+Shift+P -> "dev:mcp"
# Or manually:
uvicorn mcp-server.server:app --reload --host 127.0.0.1 --port 8000
```

## Available Commands

Use `Cmd+Shift+P` to access these commands:

- `dev:mcp` - Start MCP server
- `test` - Run all tests
- `test:security` - Run security tests
- `test:integration` - Run integration tests
- `eval` - Run evaluation with default dataset
- `eval:full` - Run full evaluation with output
- `obs:ingest` - Ingest audit logs
- `obs:audit` - View recent audit events
- `lint` - Run linting
- `format` - Format code
- `format:check` - Check formatting
- `docs:check` - Check documentation version headers
- `health` - Check server health

## Using @docs

Cursor can reference external documentation:

1. **Add docs**: Use `@Add` to include external documentation
2. **Reference docs**: Use `@docs` to reference added documentation
3. **Generate docs**: Ask Cursor to generate documentation from code

### Example

```
@docs Please generate API documentation for the summarize endpoint
```

## Project Guardrails

The project follows strict guardrails defined in `.cursor/rules/project-guardrails.mdc`:

### Always
- Use only whitelisted MCP tools
- Run tests after code changes
- Keep documentation current
- Follow Black formatting (single source of truth)
- Use conventional commits

### Never
- Expose secrets or touch `.env*` files
- Edit `app/` or `lab/` during code freeze
- Disable security policies
- Bypass audit logging

### Code Freeze Rules
During `ops/cursor-setup-and-audit-*` branches:
- **ONLY** edit: `.cursor/**`, `.github/**`, `docs/**`, `pyproject.toml`, `requirements*.txt`, `README.md`, `CHANGELOG.md`
- **FORBIDDEN**: `app/`, `lab/` (except config files)

## Security Features

### Guardian Integration
All tool calls go through Guardian security policy:
- Access control
- PII redaction
- Input validation

### Audit Logging
All operations are logged:
- Tool calls
- User actions
- Performance metrics
- Error tracking

### MCP Tool Allowlist
Only these tools are available:
- `search_docs` - Search documentation
- `summarize` - Summarize text
- `rag_query` - RAG-based queries
- `run_tests` - Execute tests
- `eval_metrics` - Evaluation metrics
- `audit_recent` - Recent audit events
- `audit_by_request` - Audit by request ID
- `audit_by_tool` - Audit by tool name

## Best Practices

### 1. Code Changes
```bash
# Always run tests after changes
test

# Check formatting
format:check

# Run security tests for security changes
test:security
```

### 2. Documentation
- Add version headers: `<!-- Version: 0.6.0 -->`
- Update README for API changes
- Include examples for new features

### 3. Evaluation
- Run `eval` for AI/ML changes
- Attach evaluation results to PRs
- Monitor performance metrics

### 4. Git Workflow
- Use feature branches
- Follow conventional commits
- Squash merge to main
- Include PR template checklist

## Troubleshooting

### MCP Server Issues
```bash
# Check server health
health

# Restart server
dev:mcp
```

### Formatting Issues
```bash
# Fix formatting
format

# Check what would be formatted
format:check
```

### Test Failures
```bash
# Run specific test
pytest lab/tests/test_specific.py -v

# Run with coverage
pytest --cov=lab lab/tests/
```

### Documentation Issues
```bash
# Check version headers
docs:check

# Find missing headers
find docs/ -name "*.md" -exec grep -L "<!-- Version:" {} \;
```

## Advanced Usage

### Custom Commands
Add custom commands to `.cursor/environment.json`:

```json
{
  "commands": {
    "custom:command": "your-command-here"
  }
}
```

### MCP Tool Development
1. Add new tool to MCP server
2. Update `.cursor/mcp.json` allowlist
3. Test with `health` command
4. Update documentation

### Documentation Generation
Use Cursor to generate docs from code:

```
@docs Generate API documentation for all endpoints in mcp-server/server.py
```

## Resources

- [Cursor Documentation](https://docs.cursor.com/)
- [MCP Protocol](https://modelcontextprotocol.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Project Architecture](docs/architecture/)
