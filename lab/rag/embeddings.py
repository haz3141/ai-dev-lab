"""
RAG Embeddings Module - Step 6A

Handles embedding generation and storage for RAG baseline.
"""

import numpy as np
from typing import List, Dict, Any
import logging
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """Generates embeddings for text chunks."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the embedding generator.

        Args:
            model_name: Name of the sentence transformer model
        """
        self.model_name = model_name
        self.model = None
        self.embedding_dim = 384  # Default for all-MiniLM-L6-v2

    def _load_model(self):
        """Lazy load the sentence transformer model."""
        if self.model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self.model = SentenceTransformer(self.model_name)
                logger.info("Loaded embedding model: %s", self.model_name)
            except ImportError:
                logger.error("sentence-transformers not installed. "
                             "Using mock embeddings.")
                self.model = None

    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text.

        Args:
            text: Input text

        Returns:
            Embedding vector as numpy array
        """
        self._load_model()

        if self.model is None:
            # Mock embedding for testing
            return self._generate_mock_embedding(text)

        embedding = self.model.encode(text)
        return embedding

    def generate_embeddings_batch(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of input texts

        Returns:
            Array of embedding vectors
        """
        self._load_model()

        if self.model is None:
            # Mock embeddings for testing
            return np.array([self._generate_mock_embedding(text)
                             for text in texts])

        embeddings = self.model.encode(texts)
        return embeddings

    def _generate_mock_embedding(self, text: str) -> np.ndarray:
        """Generate a deterministic mock embedding for testing."""
        # Use text hash to create deterministic mock embedding
        import hashlib
        hash_obj = hashlib.md5(text.encode())
        hash_bytes = hash_obj.digest()

        # Convert hash to embedding-like vector
        embedding = np.frombuffer(hash_bytes, dtype=np.float32)

        # Pad or truncate to match expected dimension
        if len(embedding) < self.embedding_dim:
            padding = np.random.RandomState(42).normal(
                0, 0.1, self.embedding_dim - len(embedding))
            embedding = np.concatenate([embedding, padding])
        else:
            embedding = embedding[:self.embedding_dim]

        # Normalize to unit vector
        embedding = embedding / np.linalg.norm(embedding)
        return embedding


class EmbeddingStore:
    """Stores and retrieves embeddings with metadata."""

    def __init__(self, store_path: str = "data/embeddings"):
        """
        Initialize the embedding store.

        Args:
            store_path: Path to store embeddings and metadata
        """
        self.store_path = Path(store_path)
        self.store_path.mkdir(parents=True, exist_ok=True)
        self.embeddings_file = self.store_path / "embeddings.npy"
        self.metadata_file = self.store_path / "metadata.json"

        self.embeddings = None
        self.metadata = []
        self._load_existing()

    def _load_existing(self):
        """Load existing embeddings and metadata."""
        if self.embeddings_file.exists() and self.metadata_file.exists():
            try:
                self.embeddings = np.load(self.embeddings_file)
                with open(self.metadata_file, 'r') as f:
                    self.metadata = json.load(f)
                logger.info("Loaded %d existing embeddings", len(self.metadata))
            except Exception as e:
                logger.error("Failed to load existing embeddings: %s", e)
                self.embeddings = None
                self.metadata = []

    def add_embeddings(self, embeddings: np.ndarray,
                       metadata: List[Dict[str, Any]]):
        """
        Add new embeddings and metadata to the store.

        Args:
            embeddings: Array of embedding vectors
            metadata: List of metadata dictionaries
        """
        if self.embeddings is None:
            self.embeddings = embeddings
        else:
            self.embeddings = np.vstack([self.embeddings, embeddings])

        self.metadata.extend(metadata)
        self._save()
        logger.info("Added %d embeddings to store", len(embeddings))

    def search_similar(self, query_embedding: np.ndarray,
                       top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar embeddings.

        Args:
            query_embedding: Query embedding vector
            top_k: Number of top results to return

        Returns:
            List of metadata dictionaries with similarity scores
        """
        if self.embeddings is None or len(self.embeddings) == 0:
            return []

        # Compute cosine similarities
        similarities = np.dot(self.embeddings, query_embedding)

        # Get top-k indices
        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = []
        for idx in top_indices:
            result = self.metadata[idx].copy()
            result['similarity_score'] = float(similarities[idx])
            result['embedding_index'] = int(idx)
            results.append(result)

        return results

    def _save(self):
        """Save embeddings and metadata to disk."""
        try:
            np.save(self.embeddings_file, self.embeddings)
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2)
            logger.info("Saved embeddings to %s", self.store_path)
        except Exception as e:
            logger.error("Failed to save embeddings: %s", e)

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the embedding store."""
        return {
            "total_embeddings": len(self.metadata) if self.metadata else 0,
            "embedding_dimension": (self.embeddings.shape[1]
                                    if self.embeddings is not None else 0),
            "store_path": str(self.store_path)
        }


def process_documents_for_rag(documents: List[Dict[str, Any]],
                             store_path: str = "data/embeddings") -> EmbeddingStore:
    """
    Process a list of documents for RAG by generating embeddings.

    Args:
        documents: List of documents with 'content' and 'metadata' keys
        store_path: Path to store embeddings

    Returns:
        EmbeddingStore instance with processed embeddings
    """
    generator = EmbeddingGenerator()
    store = EmbeddingStore(store_path)

    texts = [doc['content'] for doc in documents]
    metadata = [doc['metadata'] for doc in documents]

    logger.info("Generating embeddings for %d documents", len(documents))
    embeddings = generator.generate_embeddings_batch(texts)

    store.add_embeddings(embeddings, metadata)
    return store
