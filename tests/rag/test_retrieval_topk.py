"""Tests for RAG retrieval tool - Step 6B

Tests top-k retrieval functionality with deterministic behavior.
"""

from unittest.mock import Mock, patch

from mcp_server.tools.search_docs import DocumentSearchTool, search_documents_endpoint


class TestDocumentSearchTool:
    """Test the document search tool functionality."""

    def test_mock_search_results(self):
        """Test that mock search results are generated correctly."""
        tool = DocumentSearchTool()

        query = "test query"
        results = tool._mock_search_results(query, top_k=3)

        assert len(results) == 3

        # Check result structure
        for i, result in enumerate(results):
            assert result["rank"] == i + 1
            assert result["chunk_id"] == f"mock_chunk_{i}"
            assert result["doc_id"] == f"mock_doc_{i}"
            assert query in result["content"]
            assert result["similarity_score"] == 0.9 - (i * 0.1)
            assert "metadata" in result
            assert result["metadata"]["word_count"] == 50 + (i * 10)

    def test_mock_search_top_k_limit(self):
        """Test that top_k parameter limits results correctly."""
        tool = DocumentSearchTool()

        # Request more than available mock results
        results = tool._mock_search_results("test", top_k=10)

        # Should only return 3 mock results (the limit)
        assert len(results) <= 3

    def test_search_documents_fallback(self):
        """Test that search_documents falls back to mock when components unavailable."""
        # Create tool with unavailable components
        tool = DocumentSearchTool()
        tool.embedding_store = None
        tool.embedding_generator = None

        results = tool.search_documents("test query", top_k=2)

        assert len(results) == 2
        assert all("mock" in result["chunk_id"] for result in results)

    @patch("mcp_server.tools.search_docs.EmbeddingStore")
    @patch("mcp_server.tools.search_docs.EmbeddingGenerator")
    def test_search_documents_with_components(self, mock_generator_class, mock_store_class):
        """Test search_documents with mocked RAG components."""
        # Mock the components
        mock_generator = Mock()
        mock_store = Mock()
        mock_generator_class.return_value = mock_generator
        mock_store_class.return_value = mock_store

        # Mock embedding generation
        mock_embedding = [0.1, 0.2, 0.3]
        mock_generator.generate_embedding.return_value = mock_embedding

        # Mock search results
        mock_search_results = [
            {
                "chunk_id": "test_chunk_1",
                "doc_id": "test_doc_1",
                "content": "Test content 1",
                "similarity_score": 0.95,
                "word_count": 100,
                "chunk_number": 0,
                "source_file": "test1.txt",
            },
            {
                "chunk_id": "test_chunk_2",
                "doc_id": "test_doc_2",
                "content": "Test content 2",
                "similarity_score": 0.85,
                "word_count": 80,
                "chunk_number": 1,
                "source_file": "test2.txt",
            },
        ]
        mock_store.search_similar.return_value = mock_search_results

        # Create tool and force component loading
        tool = DocumentSearchTool()
        tool.embedding_generator = mock_generator
        tool.embedding_store = mock_store

        # Test search
        results = tool.search_documents("test query", top_k=2)

        # Verify calls
        mock_generator.generate_embedding.assert_called_once_with("test query")
        mock_store.search_similar.assert_called_once_with(mock_embedding, 2)

        # Verify results format
        assert len(results) == 2
        assert results[0]["rank"] == 1
        assert results[0]["chunk_id"] == "test_chunk_1"
        assert results[0]["similarity_score"] == 0.95
        assert results[1]["rank"] == 2
        assert results[1]["chunk_id"] == "test_chunk_2"
        assert results[1]["similarity_score"] == 0.85

    def test_get_search_stats_unavailable(self):
        """Test search stats when components are unavailable."""
        tool = DocumentSearchTool()
        tool.embedding_store = None

        stats = tool.get_search_stats()

        assert stats["status"] == "unavailable"
        assert stats["total_documents"] == 0
        assert stats["embedding_dimension"] == 0

    @patch("mcp_server.tools.search_docs.EmbeddingStore")
    def test_get_search_stats_available(self, mock_store_class):
        """Test search stats when components are available."""
        mock_store = Mock()
        mock_store_class.return_value = mock_store

        # Mock stats
        mock_stats = {
            "total_embeddings": 100,
            "embedding_dimension": 384,
            "store_path": "/test/path",
        }
        mock_store.get_stats.return_value = mock_stats

        tool = DocumentSearchTool()
        tool.embedding_store = mock_store

        stats = tool.get_search_stats()

        assert stats["status"] == "available"
        assert stats["total_embeddings"] == 100
        assert stats["embedding_dimension"] == 384


class TestSearchEndpoint:
    """Test the MCP endpoint functions."""

    def test_search_documents_endpoint_success(self):
        """Test successful search endpoint call."""
        with patch("mcp_server.tools.search_docs.search_tool") as mock_tool:
            # Mock search results
            mock_results = [{"rank": 1, "chunk_id": "chunk1", "content": "test content"}]
            mock_tool.search_documents.return_value = mock_results
            mock_tool.get_search_stats.return_value = {"status": "available"}

            result = search_documents_endpoint("test query", top_k=5)

            assert result["query"] == "test query"
            assert result["results"] == mock_results
            assert result["total_results"] == 1
            assert "search_stats" in result

    def test_search_documents_endpoint_error(self):
        """Test search endpoint error handling."""
        with patch("mcp_server.tools.search_docs.search_tool") as mock_tool:
            # Mock error
            mock_tool.search_documents.side_effect = Exception("Test error")

            result = search_documents_endpoint("test query")

            assert result["query"] == "test query"
            assert result["results"] == []
            assert result["total_results"] == 0
            assert "error" in result

    def test_search_documents_endpoint_default_params(self):
        """Test search endpoint with default parameters."""
        with patch("mcp_server.tools.search_docs.search_tool") as mock_tool:
            mock_tool.search_documents.return_value = []
            mock_tool.get_search_stats.return_value = {}
            search_documents_endpoint("test query")

            # Should call with default top_k=5
            mock_tool.search_documents.assert_called_once_with("test query", 5)


class TestSearchHealth:
    """Test search health functionality."""

    def test_get_search_health_healthy(self):
        """Test health check when search is available."""
        with patch("mcp_server.tools.search_docs.search_tool") as mock_tool:
            mock_tool.get_search_stats.return_value = {
                "status": "available",
                "total_documents": 50,
                "embedding_dimension": 384,
                "store_path": "/test/path",
            }

            from mcp_server.tools.search_docs import get_search_health

            health = get_search_health()

            assert health["status"] == "healthy"
            assert health["search_available"] is True
            assert health["total_documents"] == 50
            assert health["embedding_dimension"] == 384

    def test_get_search_health_degraded(self):
        """Test health check when search is unavailable."""
        with patch("mcp_server.tools.search_docs.search_tool") as mock_tool:
            mock_tool.get_search_stats.return_value = {
                "status": "unavailable",
                "total_documents": 0,
                "embedding_dimension": 0,
            }

            from mcp_server.tools.search_docs import get_search_health

            health = get_search_health()

            assert health["status"] == "degraded"
            assert health["search_available"] is False
            assert health["total_documents"] == 0

    def test_get_search_health_error(self):
        """Test health check error handling."""
        with patch("mcp_server.tools.search_docs.search_tool") as mock_tool:
            mock_tool.get_search_stats.side_effect = Exception("Test error")

            from mcp_server.tools.search_docs import get_search_health

            health = get_search_health()

            assert health["status"] == "unhealthy"
            assert health["search_available"] is False
            assert "error" in health


class TestIntegration:
    """Integration tests for the complete retrieval system."""

    def test_deterministic_ranking(self):
        """Test that search results have consistent ranking."""
        tool = DocumentSearchTool()

        # Run same search multiple times
        query = "machine learning algorithms"
        results1 = tool._mock_search_results(query, top_k=3)
        results2 = tool._mock_search_results(query, top_k=3)

        # Results should be identical
        assert len(results1) == len(results2)
        for r1, r2 in zip(results1, results2, strict=False):
            assert r1["rank"] == r2["rank"]
            assert r1["chunk_id"] == r2["chunk_id"]
            assert r1["similarity_score"] == r2["similarity_score"]

    def test_score_ordering(self):
        """Test that results are ordered by similarity score."""
        tool = DocumentSearchTool()

        results = tool._mock_search_results("test", top_k=3)

        # Scores should be in descending order
        scores = [result["similarity_score"] for result in results]
        assert scores == sorted(scores, reverse=True)

        # Ranks should be in ascending order
        ranks = [result["rank"] for result in results]
        assert ranks == sorted(ranks)
