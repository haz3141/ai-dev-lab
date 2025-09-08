# mcp_server/simple_server.py
from mcp_server.app import app
from mcp_server.tools.git_guardrails import register as reg_git
from mcp_server.tools.ping import register as reg_ping
from mcp_server.tools.search_docs import register as reg_search
from mcp_server.tools.summarize import register as reg_sum

# Explicitly register all tools with the ONE app instance
reg_ping(app)
reg_search(app)
reg_sum(app)
reg_git(app)

if __name__ == "__main__":
    # IMPORTANT: stdio transport; no prints to stdout anywhere else
    app.run(transport="stdio")
