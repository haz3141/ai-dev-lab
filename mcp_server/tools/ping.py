from mcp.server.fastmcp import FastMCP

app = FastMCP.current()


@app.tool()
def ping(message: str = "ok") -> str:
    """Health check tool; returns the input message."""
    return message
