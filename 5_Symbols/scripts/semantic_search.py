#!/usr/bin/env python3
"""
Semantic Search Script - Search codebase using Qdrant semantic search

This script reads a query from the clipboard, performs semantic search
on the indexed codebase, and returns formatted results to the clipboard.
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from utils.logger import setup_logger
from utils.qdrant_manager import QdrantManager
from utils.clipboard_manager import get_clipboard, set_clipboard
from utils.notification import show_notification

logger = setup_logger('semantic_search')


def main():
    """Main function for semantic search."""
    try:
        logger.info("Starting semantic search")

        # Get query from clipboard
        query = get_clipboard()
        if not query or not query.strip():
            msg = "No query found in clipboard. Copy your search query first."
            logger.warning(msg)
            show_notification("Semantic Search", msg)
            return 1

        query = query.strip()
        logger.info(f"Search query: {query}")

        # Initialize Qdrant manager
        manager = QdrantManager()

        # Health check
        healthy, health_msg = manager.health_check()
        if not healthy:
            logger.error(f"Health check failed: {health_msg}")
            show_notification("Semantic Search Error", f"Services not ready: {health_msg}")
            return 1

        # Get collection info
        info = manager.collection_info()
        if not info or info.get('points_count', 0) == 0:
            msg = "Collection is empty. Run indexing first."
            logger.warning(msg)
            show_notification("Semantic Search", msg)
            return 1

        logger.info(f"Collection has {info['points_count']} indexed chunks")

        # Perform search
        show_notification("Semantic Search", f"Searching for: {query[:50]}...")
        results = manager.search(query, limit=5, score_threshold=0.3)

        if not results:
            msg = "No results found. Try a different query."
            logger.info(msg)
            set_clipboard(f"Search query: {query}\n\n{msg}")
            show_notification("Semantic Search", msg)
            return 0

        # Format results
        formatted = manager.format_results(results, max_content_length=300)
        logger.info(f"Found {len(results)} results")

        # Add header with query and stats
        output = [
            "=" * 80,
            "SEMANTIC SEARCH RESULTS",
            "=" * 80,
            f"Query: {query}",
            f"Collection: {info['name']}",
            f"Total indexed chunks: {info['points_count']}",
            "=" * 80,
            "",
            formatted
        ]

        result_text = '\n'.join(output)

        # Copy to clipboard
        set_clipboard(result_text)
        logger.info("Results copied to clipboard")

        # Show notification
        show_notification(
            "Semantic Search Complete",
            f"Found {len(results)} results. Results copied to clipboard."
        )

        return 0

    except Exception as e:
        logger.error(f"Error during semantic search: {e}", exc_info=True)
        show_notification("Semantic Search Error", str(e))
        return 1


if __name__ == "__main__":
    sys.exit(main())
