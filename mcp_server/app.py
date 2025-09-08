# mcp_server/app.py
import logging
import sys

from mcp.server.fastmcp import FastMCP

# All logs -> stderr; stdout reserved for JSON-RPC
logging.basicConfig(stream=sys.stderr, level=logging.INFO)

# SINGLE shared app instance for the whole server
app = FastMCP(name="lab-server")
