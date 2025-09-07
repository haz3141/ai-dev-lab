"""RAG Ingestion Module - Step 6A

Handles document ingestion, chunking, and embedding generation for RAG.
"""

import hashlib
import logging
import os
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class DocumentChunk:
    """Represents a chunk of a document with metadata."""

    content: str
    chunk_id: str
    doc_id: str
    start_pos: int
    end_pos: int
    metadata: dict[str, Any]


class DocumentIngester:
    """Handles document ingestion and chunking."""

    def __init__(self, chunk_size: int = 1000, overlap: float = 0.15):
        """Initialize the document ingester.

        Args:
            chunk_size: Maximum tokens per chunk (approximate)
            overlap: Overlap ratio between chunks (0.15 = 15%)
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.overlap_tokens = int(chunk_size * overlap)

    def chunk_text(self, text: str, doc_id: str) -> list[DocumentChunk]:
        """Split text into overlapping chunks.

        Args:
            text: Input text to chunk
            doc_id: Document identifier

        Returns:
            List of document chunks with metadata
        """
        chunks = []
        words = text.split()

        if len(words) <= self.chunk_size:
            # Single chunk for short documents
            chunk_id = self._generate_chunk_id(doc_id, 0, len(words))
            chunk = DocumentChunk(
                content=text,
                chunk_id=chunk_id,
                doc_id=doc_id,
                start_pos=0,
                end_pos=len(text),
                metadata={"word_count": len(words)},
            )
            chunks.append(chunk)
            return chunks

        # Multi-chunk processing
        start_idx = 0
        chunk_num = 0

        while start_idx < len(words):
            end_idx = min(start_idx + self.chunk_size, len(words))
            chunk_words = words[start_idx:end_idx]
            chunk_text = " ".join(chunk_words)

            chunk_id = self._generate_chunk_id(doc_id, chunk_num, len(chunk_words))
            chunk = DocumentChunk(
                content=chunk_text,
                chunk_id=chunk_id,
                doc_id=doc_id,
                start_pos=start_idx,
                end_pos=end_idx,
                metadata={
                    "word_count": len(chunk_words),
                    "chunk_number": chunk_num,
                    "total_chunks": ((len(words) + self.chunk_size - 1) // self.chunk_size),
                },
            )
            chunks.append(chunk)

            # Move start position with overlap
            start_idx = end_idx - self.overlap_tokens
            chunk_num += 1

            # Prevent infinite loop
            if start_idx >= len(words) - self.overlap_tokens:
                break

        return chunks

    def _generate_chunk_id(self, doc_id: str, chunk_num: int, word_count: int) -> str:
        """Generate a unique chunk ID."""
        content = f"{doc_id}_{chunk_num}_{word_count}"
        return hashlib.md5(content.encode()).hexdigest()[:12]

    def ingest_document(
        self,
        content: str,
        doc_id: str,
        metadata: dict[str, Any] = None,
    ) -> list[DocumentChunk]:
        """Ingest a single document and return chunks.

        Args:
            content: Document content
            doc_id: Document identifier
            metadata: Additional metadata for the document

        Returns:
            List of document chunks
        """
        if metadata is None:
            metadata = {}

        chunks = self.chunk_text(content, doc_id)

        # Add document-level metadata to each chunk
        for chunk in chunks:
            chunk.metadata.update(metadata)

        logger.info("Ingested document %s into %d chunks", doc_id, len(chunks))
        return chunks


def ingest_from_file(file_path: str, doc_id: str = None) -> list[DocumentChunk]:
    """Ingest a document from a file.

    Args:
        file_path: Path to the file
        doc_id: Document ID (defaults to filename)

    Returns:
        List of document chunks
    """
    if doc_id is None:
        doc_id = os.path.basename(file_path)

    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    ingester = DocumentIngester()
    return ingester.ingest_document(content, doc_id, {"source_file": file_path})


def ingest_from_directory(dir_path: str, file_extensions: list[str] = None) -> list[DocumentChunk]:
    """Ingest all documents from a directory.

    Args:
        dir_path: Directory path
        file_extensions: List of file extensions to include

    Returns:
        List of all document chunks
    """
    if file_extensions is None:
        file_extensions = [".txt", ".md"]

    all_chunks = []

    for root, _, files in os.walk(dir_path):
        for file in files:
            if any(file.endswith(ext) for ext in file_extensions):
                file_path = os.path.join(root, file)
                try:
                    chunks = ingest_from_file(file_path)
                    all_chunks.extend(chunks)
                except Exception as e:
                    logger.error("Failed to ingest %s: %s", file_path, e)

    logger.info("Ingested %d documents from %s", len(all_chunks), dir_path)
    return all_chunks
