from pathlib import Path

from mcp.server.fastmcp import FastMCP

app = FastMCP.current()


@app.tool()
def search_docs(query: str, root: str = ".", max_results: int = 5) -> dict:
    """Naive read-only search over text/markdown files.
    Returns { matches: [ {file, line, text} ] }.
    """
    q = (query or "").strip().lower()
    if not q:
        return {"matches": []}

    root_path = Path(root)
    exts = {".md", ".txt", ".py"}
    matches = []

    for p in root_path.rglob("*"):
        if p.is_file() and p.suffix in exts and p.stat().st_size <= 256_000:
            try:
                content = p.read_text(errors="ignore")
            except (OSError, PermissionError):
                continue
            for i, line in enumerate(content.splitlines(), 1):
                if q in line.lower():
                    matches.append({"file": str(p), "line": i, "text": line.strip()})
                    if len(matches) >= max_results:
                        return {"matches": matches}

    return {"matches": matches}
