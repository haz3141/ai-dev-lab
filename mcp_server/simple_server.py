import logging
import sys

from mcp.server.fastmcp import FastMCP

# Logs to stderr only; stdout reserved for JSON-RPC
logging.basicConfig(stream=sys.stderr, level=logging.INFO)

app = FastMCP(name="lab-server")

# --- Tool registrations ---
from mcp_server.tools.ping import ping  # noqa: E402,F401
from mcp_server.tools.search_docs import search_docs  # noqa: E402,F401
from mcp_server.tools.summarize import summarize  # noqa: E402,F401

# FastMCP decorator registration occurs in the tool modules.

if __name__ == "__main__":
    # stdio transport; no prints to stdout anywhere else
    app.run(transport="stdio")
