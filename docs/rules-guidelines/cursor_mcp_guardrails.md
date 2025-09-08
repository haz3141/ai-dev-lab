<!--
Version: 0.6.4
-->
# Cursor + MCP Guardrails (Team)

- Freeze-first workflow: repo is read-only unless the operator types `WRITE OK`.
- Cursor Agent must request approval before running tools or applying edits.
- MCP server uses **stdio**; **no stdout prints** (logs → stderr).
- Tool allowlist during setup: `ping`, `search_docs`, `summarize`.
- Keep outputs concise and structured; avoid large dumps.
