# mcp_server/tools/ping.py
def register(app):
    @app.tool()
    def ping(message: str = "ok") -> str:
        """Health check tool; echoes the input."""
        return message
