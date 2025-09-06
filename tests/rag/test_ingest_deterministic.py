"""
Deterministic tests for RAG ingestion - Step 6A

Tests chunking and embedding generation with fixed seeds and inputs.
"""

import numpy as np
from lab.rag.ingest import DocumentIngester
from lab.rag.embeddings import EmbeddingGenerator, EmbeddingStore


class TestDocumentIngestion:
    """Test document ingestion and chunking."""

    def test_single_chunk_document(self):
        """Test that short documents create single chunks."""
        ingester = DocumentIngester(chunk_size=1000, overlap=0.15)

        text = "This is a short document with only a few words."
        doc_id = "test_doc_1"

        chunks = ingester.chunk_text(text, doc_id)

        assert len(chunks) == 1
        assert chunks[0].content == text
        assert chunks[0].doc_id == doc_id
        assert chunks[0].chunk_id is not None
        assert chunks[0].metadata["word_count"] == 10

    def test_multi_chunk_document(self):
        """Test that long documents are split into multiple chunks."""
        ingester = DocumentIngester(chunk_size=10, overlap=0.2)

        # Create a document with 25 words (should create 3 chunks)
        words = [f"word_{i}" for i in range(25)]
        text = " ".join(words)
        doc_id = "test_doc_2"

        chunks = ingester.chunk_text(text, doc_id)

        # Should have 3 chunks with overlap
        assert len(chunks) >= 2  # At least 2 chunks for 25 words with size 10

        # Check chunk properties
        for i, chunk in enumerate(chunks):
            assert chunk.doc_id == doc_id
            assert chunk.chunk_id is not None
            assert chunk.metadata["word_count"] <= 10
            assert chunk.metadata["chunk_number"] == i

    def test_chunk_overlap(self):
        """Test that chunks have proper overlap."""
        ingester = DocumentIngester(chunk_size=10, overlap=0.2)

        # Create a document that will definitely need multiple chunks
        words = [f"word_{i}" for i in range(30)]
        text = " ".join(words)
        doc_id = "test_doc_3"

        chunks = ingester.chunk_text(text, doc_id)

        if len(chunks) > 1:
            # Check that chunks have overlap
            first_chunk_words = chunks[0].content.split()
            second_chunk_words = chunks[1].content.split()

            # Should have some overlap (at least 2 words with 20% overlap)
            overlap_words = set(first_chunk_words) & set(second_chunk_words)
            assert len(overlap_words) >= 2

    def test_deterministic_chunk_ids(self):
        """Test that chunk IDs are deterministic."""
        ingester = DocumentIngester()

        text = "This is a test document for deterministic chunking."
        doc_id = "test_doc_4"

        chunks1 = ingester.chunk_text(text, doc_id)
        chunks2 = ingester.chunk_text(text, doc_id)

        # Chunk IDs should be identical
        assert len(chunks1) == len(chunks2)
        for c1, c2 in zip(chunks1, chunks2):
            assert c1.chunk_id == c2.chunk_id
            assert c1.content == c2.content


class TestEmbeddingGeneration:
    """Test embedding generation with deterministic behavior."""

    def test_mock_embedding_deterministic(self):
        """Test that mock embeddings are deterministic."""
        generator = EmbeddingGenerator()

        text = "This is a test text for deterministic embeddings."

        # Generate embeddings multiple times
        emb1 = generator.generate_embedding(text)
        emb2 = generator.generate_embedding(text)

        # Should be identical
        np.testing.assert_array_equal(emb1, emb2)

        # Should have correct dimension
        assert emb1.shape == (384,)
        assert emb2.shape == (384,)

    def test_embedding_normalization(self):
        """Test that embeddings are normalized to unit vectors."""
        generator = EmbeddingGenerator()

        text = "Test text for normalization check."
        embedding = generator.generate_embedding(text)

        # Should be normalized (unit vector)
        norm = np.linalg.norm(embedding)
        assert abs(norm - 1.0) < 1e-6

    def test_batch_embeddings(self):
        """Test batch embedding generation."""
        generator = EmbeddingGenerator()

        texts = [
            "First test text.",
            "Second test text.",
            "Third test text."
        ]

        embeddings = generator.generate_embeddings_batch(texts)

        assert embeddings.shape == (3, 384)

        # Each embedding should be normalized
        for i in range(3):
            norm = np.linalg.norm(embeddings[i])
            assert abs(norm - 1.0) < 1e-6


class TestEmbeddingStore:
    """Test embedding storage and retrieval."""

    def test_empty_store(self):
        """Test behavior with empty store."""
        store = EmbeddingStore("test_empty_store")

        query = np.random.randn(384)
        query = query / np.linalg.norm(query)  # Normalize

        results = store.search_similar(query, top_k=5)
        assert results == []

    def test_add_and_search(self):
        """Test adding embeddings and searching."""
        store = EmbeddingStore("test_add_search")

        # Create test embeddings
        embeddings = np.random.randn(3, 384)
        # Normalize each embedding
        for i in range(3):
            embeddings[i] = embeddings[i] / np.linalg.norm(embeddings[i])

        metadata = [
            {"chunk_id": "chunk_1", "content": "First chunk"},
            {"chunk_id": "chunk_2", "content": "Second chunk"},
            {"chunk_id": "chunk_3", "content": "Third chunk"}
        ]

        store.add_embeddings(embeddings, metadata)

        # Search with first embedding as query
        query = embeddings[0]
        results = store.search_similar(query, top_k=2)

        assert len(results) == 2
        # Should be most similar to itself
        assert results[0]["chunk_id"] == "chunk_1"
        assert "similarity_score" in results[0]
        # Should be very similar to itself
        assert results[0]["similarity_score"] > 0.99

    def test_deterministic_search_order(self):
        """Test that search results are deterministic."""
        store = EmbeddingStore("test_deterministic_search")

        # Create identical embeddings
        embedding = np.random.randn(384)
        embedding = embedding / np.linalg.norm(embedding)

        embeddings = np.tile(embedding, (3, 1))
        metadata = [
            {"chunk_id": "chunk_1", "content": "First"},
            {"chunk_id": "chunk_2", "content": "Second"},
            {"chunk_id": "chunk_3", "content": "Third"}
        ]

        store.add_embeddings(embeddings, metadata)

        # Search multiple times
        query = embedding
        results1 = store.search_similar(query, top_k=3)
        results2 = store.search_similar(query, top_k=3)

        # Results should be identical
        assert len(results1) == len(results2)
        for r1, r2 in zip(results1, results2):
            assert r1["chunk_id"] == r2["chunk_id"]
            assert abs(r1["similarity_score"] - r2["similarity_score"]) < 1e-6


class TestIntegration:
    """Integration tests for the complete ingestion pipeline."""

    def test_full_pipeline(self):
        """Test the complete document ingestion and embedding pipeline."""
        from lab.rag.embeddings import process_documents_for_rag

        # Create test documents
        documents = [
            {
                "content": "This is the first test document about machine learning.",
                "metadata": {"doc_id": "doc_1", "title": "ML Document"}
            },
            {
                "content": "This is the second test document about natural language processing.",
                "metadata": {"doc_id": "doc_2", "title": "NLP Document"}
            }
        ]

        # Process documents
        store = process_documents_for_rag(documents, "test_pipeline_store")

        # Check store stats
        stats = store.get_stats()
        assert stats["total_embeddings"] == 2
        assert stats["embedding_dimension"] == 384

        # Test search
        generator = EmbeddingGenerator()
        query_text = "machine learning algorithms"
        query_embedding = generator.generate_embedding(query_text)

        results = store.search_similar(query_embedding, top_k=1)
        assert len(results) == 1
        # Should match ML document
        assert results[0]["doc_id"] == "doc_1"
