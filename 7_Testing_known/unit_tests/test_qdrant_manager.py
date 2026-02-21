#!/usr/bin/env python3
"""
Unit tests for QdrantManager
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "5_Symbols"))

from utils.qdrant_manager import QdrantManager, SearchResult


class TestQdrantManager(unittest.TestCase):
    """Test cases for QdrantManager class."""

    @patch('utils.qdrant_manager.QdrantClient')
    def setUp(self, mock_client_class):
        """Set up test fixtures."""
        self.mock_client = Mock()
        mock_client_class.return_value = self.mock_client
        self.manager = QdrantManager()

    @patch('utils.qdrant_manager.requests.get')
    def test_health_check_success(self, mock_get):
        """Test successful health check."""
        # Mock Qdrant response
        qdrant_response = Mock()
        qdrant_response.status_code = 200
        qdrant_response.text = "qdrant"
        qdrant_response.json.return_value = {"version": "1.7.0"}

        # Mock Ollama response
        ollama_response = Mock()
        ollama_response.status_code = 200
        ollama_response.json.return_value = {
            "models": [{"name": "nomic-embed-text:v1.5"}]
        }

        # Set up mock to return different responses based on URL
        def get_side_effect(url, *args, **kwargs):
            if "6333" in url:
                return qdrant_response
            elif "11434" in url:
                return ollama_response

        mock_get.side_effect = get_side_effect

        healthy, message = self.manager.health_check()
        self.assertTrue(healthy)
        self.assertEqual(message, "All services healthy")

    @patch('utils.qdrant_manager.requests.get')
    def test_health_check_ollama_down(self, mock_get):
        """Test health check when Ollama is down."""
        # Mock Qdrant success
        qdrant_response = Mock()
        qdrant_response.status_code = 200
        qdrant_response.text = "qdrant"
        qdrant_response.json.return_value = {"version": "1.7.0"}

        def get_side_effect(url, *args, **kwargs):
            if "6333" in url:
                return qdrant_response
            elif "11434" in url:
                raise Exception("Connection refused")

        mock_get.side_effect = get_side_effect

        healthy, message = self.manager.health_check()
        self.assertFalse(healthy)
        self.assertIn("Cannot connect to Ollama", message)

    @patch('utils.qdrant_manager.requests.post')
    def test_get_embedding_success(self, mock_post):
        """Test successful embedding generation."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "embedding": [0.1, 0.2, 0.3] * 256  # 768 dimensions
        }
        mock_post.return_value = mock_response

        embedding = self.manager.get_embedding("test text")
        self.assertEqual(len(embedding), 768)
        self.assertTrue(all(isinstance(x, float) for x in embedding))

    @patch('utils.qdrant_manager.requests.post')
    def test_get_embedding_fallback(self, mock_post):
        """Test fallback embedding when Ollama fails."""
        mock_post.side_effect = Exception("Connection error")

        embedding = self.manager.get_embedding("test text")
        self.assertGreater(len(embedding), 0)
        self.assertTrue(all(isinstance(x, float) for x in embedding))

    def test_search_empty_results(self):
        """Test search with no results."""
        self.mock_client.search.return_value = []

        with patch.object(self.manager, 'get_embedding', return_value=[0.1] * 768):
            results = self.manager.search("test query")

        self.assertEqual(len(results), 0)

    def test_search_with_results(self):
        """Test search with results."""
        # Mock search result
        mock_hit = Mock()
        mock_hit.score = 0.85
        mock_hit.payload = {
            "content": "def test(): pass",
            "file_path": "test.py",
            "chunk_index": 0,
            "language": "py"
        }
        self.mock_client.search.return_value = [mock_hit]

        with patch.object(self.manager, 'get_embedding', return_value=[0.1] * 768):
            results = self.manager.search("test query", limit=5)

        self.assertEqual(len(results), 1)
        self.assertIsInstance(results[0], SearchResult)
        self.assertEqual(results[0].file_path, "test.py")
        self.assertEqual(results[0].score, 0.85)

    def test_collection_info(self):
        """Test getting collection information."""
        mock_info = Mock()
        mock_info.points_count = 1000
        mock_info.config.params.vectors.size = 768
        mock_info.config.params.vectors.distance.name = "COSINE"
        mock_info.status.name = "GREEN"

        self.mock_client.get_collection.return_value = mock_info

        info = self.manager.collection_info()
        self.assertEqual(info['points_count'], 1000)
        self.assertEqual(info['vector_size'], 768)
        self.assertEqual(info['distance'], "COSINE")

    def test_format_results_empty(self):
        """Test formatting empty results."""
        formatted = self.manager.format_results([])
        self.assertEqual(formatted, "No results found.")

    def test_format_results_with_data(self):
        """Test formatting results with data."""
        results = [
            SearchResult(
                content="def hello():\n    print('world')",
                file_path="test.py",
                chunk_index=0,
                score=0.95,
                language="py",
                metadata={}
            )
        ]

        formatted = self.manager.format_results(results)
        self.assertIn("test.py", formatted)
        self.assertIn("0.95", formatted)
        self.assertIn("py", formatted)

    def test_delete_collection(self):
        """Test collection deletion."""
        self.mock_client.delete_collection.return_value = True

        result = self.manager.delete_collection()
        self.assertTrue(result)
        self.mock_client.delete_collection.assert_called_once()

    def test_create_collection(self):
        """Test collection creation."""
        self.mock_client.create_collection.return_value = True

        result = self.manager.create_collection()
        self.assertTrue(result)
        self.mock_client.create_collection.assert_called_once()

    def test_get_statistics(self):
        """Test getting statistics."""
        # Mock collection info
        mock_info = Mock()
        mock_info.points_count = 100
        mock_info.config.params.vectors.size = 768
        mock_info.config.params.vectors.distance.name = "COSINE"
        mock_info.status.name = "GREEN"
        self.mock_client.get_collection.return_value = mock_info

        # Mock scroll results
        mock_point1 = Mock()
        mock_point1.payload = {"language": "py", "file_path": "test1.py"}
        mock_point2 = Mock()
        mock_point2.payload = {"language": "js", "file_path": "test2.js"}

        self.mock_client.scroll.return_value = ([mock_point1, mock_point2], None)

        stats = self.manager.get_statistics()
        self.assertEqual(stats['total_chunks'], 100)
        self.assertEqual(stats['total_files'], 2)
        self.assertIn('py', stats['languages'])
        self.assertIn('js', stats['languages'])


if __name__ == '__main__':
    unittest.main()
