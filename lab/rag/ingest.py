from pathlib import Path
from typing import Iterable, Dict

def load_texts(data_dir: str) -> Iterable[Dict]:
    """Yield {'id': str, 'text': str, 'source': str} for each .txt under data_dir."""
    p = Path(data_dir)
    for f in sorted(p.glob("**/*.txt")):
        text = f.read_text(encoding="utf-8", errors="ignore")
        yield {"id": f.stem, "text": text, "source": str(f)}
