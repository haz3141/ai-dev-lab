Version: v0.6.1
# MCP Validation Evidence

## Health Check
- **Expected**: `GET /health` → 200 OK with `{"status":"ok"}`
- **Actual**: `GET /health` → 200 OK with `{"ok":true,"version":"0.6.0"}`
- **Evidence**: See `mcp-health.json` for raw response

## Allowlist Denial
- **Expected**: Non-allowlisted tools return "denied by policy".
- **Actual**: Tools return "Tool 'tools/search_docs' is not allowed by security policy"
- **Evidence**: See `mcp-deny.txt` for raw response

## Notes
- MCP server successfully running on localhost:8765
- Guardian security policy properly enforcing tool allowlist
- All tool calls are being blocked by security policy as expected
