from mcp.server.fastmcp import FastMCP

app = FastMCP.current()


@app.tool()
def summarize(text: str, max_sentences: int = 3) -> dict:
    """Deterministic extractive summary:
    - Splits on sentences.
    - Returns the first N informative sentences (no ML dependency).
    """
    if not text:
        return {"summary": ""}

    # Simple sentence split
    parts = [s.strip() for s in text.replace("\n", " ").split(".") if s.strip()]
    keep = parts[: max(1, int(max_sentences))]
    summary = ". ".join(keep)
    if text.strip().endswith("."):
        summary += "."
    return {"summary": summary}
