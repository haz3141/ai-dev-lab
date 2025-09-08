# mcp_server/tools/search_docs.py
from pathlib import Path


def register(app):
    @app.tool()
    def search_docs(query: str, root: str = ".", max_results: int = 5) -> dict:
        """Naive, read-only text search.
        Returns: { "matches": [ { "file": str, "line": int, "text": str } ] }
        """
        q = (query or "").strip().lower()
        if not q:
            return {"matches": []}

        matches, exts = [], {".md", ".txt", ".py"}
        for p in Path(root).rglob("*"):
            if p.is_file() and p.suffix in exts and p.stat().st_size <= 256_000:
                try:
                    for i, line in enumerate(p.read_text(errors="ignore").splitlines(), 1):
                        if q in line.lower():
                            matches.append({"file": str(p), "line": i, "text": line.strip()})
                            if len(matches) >= max_results:
                                return {"matches": matches}
                except OSError:
                    continue
        return {"matches": matches}
