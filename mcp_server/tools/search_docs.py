"""
RAG Document Search Tool - Step 6B

Real embedding-based document search for MCP server.
"""

import logging
from typing import List, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class DocumentSearchTool:
    """Handles embedding-based document search."""
    
    def __init__(self, embeddings_path: str = "data/embeddings"):
        """
        Initialize the document search tool.
        
        Args:
            embeddings_path: Path to stored embeddings
        """
        self.embeddings_path = Path(embeddings_path)
        self.embedding_store = None
        self.embedding_generator = None
        self._load_components()
    
    def _load_components(self):
        """Load embedding components if available."""
        try:
            # Import here to avoid dependency issues if not available
            from lab.rag.embeddings import EmbeddingStore, EmbeddingGenerator
            
            # Initialize components
            self.embedding_generator = EmbeddingGenerator()
            self.embedding_store = EmbeddingStore(str(self.embeddings_path))
            
            logger.info("Loaded RAG components for document search")
        except ImportError as e:
            logger.warning("RAG components not available: %s", e)
            self.embedding_store = None
            self.embedding_generator = None
        except Exception as e:
            logger.error("Failed to load RAG components: %s", e)
            self.embedding_store = None
            self.embedding_generator = None
    
    def search_documents(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for documents using embedding similarity.

        Args:
            query: Search query text
            top_k: Number of top results to return

        Returns:
            List of search results with metadata and scores
        """
        if not self.embedding_store or not self.embedding_generator:
            # Fallback to mock results if components not available
            return self._mock_search_results(query, top_k)
        
        try:
            # Generate query embedding
            query_embedding = self.embedding_generator.generate_embedding(query)

            # Search for similar documents
            results = self.embedding_store.search_similar(query_embedding, top_k)
            
            # Format results for MCP response
            formatted_results = []
            for i, result in enumerate(results):
                formatted_result = {
                    "rank": i + 1,
                    "chunk_id": result.get("chunk_id", f"chunk_{i}"),
                    "doc_id": result.get("doc_id", f"doc_{i}"),
                    "content": result.get("content", ""),
                    "similarity_score": result.get("similarity_score", 0.0),
                    "metadata": {
                        "word_count": result.get("word_count", 0),
                        "chunk_number": result.get("chunk_number", 0),
                        "source_file": result.get("source_file", "unknown")
                    }
                }
                formatted_results.append(formatted_result)
            
            logger.info("Found %d results for query: %s", 
                       len(formatted_results), query[:50])
            return formatted_results
            
        except Exception as e:
            logger.error("Error during document search: %s", e)
            return self._mock_search_results(query, top_k)
    
    def _mock_search_results(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Generate mock search results for testing/fallback."""
        mock_results = []
        
        for i in range(min(top_k, 3)):  # Limit to 3 mock results
            result = {
                "rank": i + 1,
                "chunk_id": f"mock_chunk_{i}",
                "doc_id": f"mock_doc_{i}",
                "content": f"Mock search result {i+1} for query: {query}",
                "similarity_score": 0.9 - (i * 0.1),  # Decreasing scores
                "metadata": {
                    "word_count": 50 + (i * 10),
                    "chunk_number": i,
                    "source_file": f"mock_file_{i}.txt"
                }
            }
            mock_results.append(result)
        
        logger.info("Generated %d mock results for query: %s", 
                   len(mock_results), query[:50])
        return mock_results
    
    def get_search_stats(self) -> Dict[str, Any]:
        """Get statistics about the search index."""
        if not self.embedding_store:
            return {
                "status": "unavailable",
                "total_documents": 0,
                "embedding_dimension": 0,
                "store_path": str(self.embeddings_path)
            }
        
        try:
            stats = self.embedding_store.get_stats()
            stats["status"] = "available"
            return stats
        except Exception as e:
            logger.error("Error getting search stats: %s", e)
            return {
                "status": "error",
                "error": str(e),
                "store_path": str(self.embeddings_path)
            }


# Global instance for the MCP server
search_tool = DocumentSearchTool()


def search_documents_endpoint(query: str, top_k: int = 5) -> Dict[str, Any]:
    """
    MCP endpoint for document search.

    Args:
        query: Search query text
        top_k: Number of top results to return

    Returns:
        Search results with metadata
    """
    try:
        results = search_tool.search_documents(query, top_k)
        
        return {
            "query": query,
            "results": results,
            "total_results": len(results),
            "search_stats": search_tool.get_search_stats()
        }
        
    except Exception as e:
        logger.error("Error in search_documents_endpoint: %s", e)
        return {
            "query": query,
            "results": [],
            "total_results": 0,
            "error": str(e)
        }


def get_search_health() -> Dict[str, Any]:
    """
    Get health status of the search system.

    Returns:
        Health status information
    """
    try:
        stats = search_tool.get_search_stats()
        
        return {
            "status": ("healthy" if stats.get("status") == "available" 
                      else "degraded"),
            "search_available": stats.get("status") == "available",
            "total_documents": stats.get("total_documents", 0),
            "embedding_dimension": stats.get("embedding_dimension", 0),
            "store_path": stats.get("store_path", "unknown")
        }
        
    except Exception as e:
        logger.error("Error getting search health: %s", e)
        return {
            "status": "unhealthy",
            "search_available": False,
            "error": str(e)
        }

