# mcp_server/tools/summarize.py
def register(app):
    @app.tool()
    def summarize(text: str, max_sentences: int = 3) -> dict:
        """Deterministic extractive summary (no model dependency)."""
        if not text:
            return {"summary": ""}

        parts = [s.strip() for s in text.replace("\n", " ").split(".") if s.strip()]
        keep = parts[: max(1, int(max_sentences))]
        summary = ". ".join(keep)
        if text.strip().endswith("."):
            summary += "."
        return {"summary": summary}
