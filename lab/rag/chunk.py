from typing import List, Dict

def simple_sentence_split(text: str) -> List[str]:
    # Naive splitter to keep tests deterministic and deps minimal.
    import re
    sents = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s for s in sents if s]

def chunk_records(records, max_chars: int = 400) -> List[Dict]:
    """Create small chunks from records; returns [{'id','text','meta'}]."""
    chunks = []
    for rec in records:
        buf = ""
        sent_id = 0
        for sent in simple_sentence_split(rec["text"]):
            if not buf:
                buf = sent
            elif len(buf) + 1 + len(sent) <= max_chars:
                buf = buf + " " + sent
            else:
                chunks.append({"id": f"{rec['id']}-{sent_id}", "text": buf, "meta": rec})
                sent_id += 1
                buf = sent
        if buf:
            chunks.append({"id": f"{rec['id']}-{sent_id}", "text": buf, "meta": rec})
    return chunks
