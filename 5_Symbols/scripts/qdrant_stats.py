#!/usr/bin/env python3
"""
Qdrant Statistics Script - Show statistics about indexed codebase

This script displays statistics about the Qdrant collection including
total chunks, files, language distribution, and collection health.
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from utils.logger import setup_logger
from utils.qdrant_manager import QdrantManager
from utils.clipboard_manager import set_clipboard
from utils.notification import show_notification

logger = setup_logger('qdrant_stats')


def main():
    """Main function for showing Qdrant statistics."""
    try:
        logger.info("Getting Qdrant statistics")

        # Initialize Qdrant manager
        manager = QdrantManager()

        # Health check
        healthy, health_msg = manager.health_check()
        health_status = "✅ Healthy" if healthy else f"❌ Issues: {health_msg}"

        # Get collection info and statistics
        info = manager.collection_info()
        stats = manager.get_statistics()

        # Format output
        output = [
            "=" * 80,
            "QDRANT SEMANTIC SEARCH STATISTICS",
            "=" * 80,
            "",
            f"Health Status: {health_status}",
            "",
            "COLLECTION INFO:",
            f"  Name: {info.get('name', 'N/A')}",
            f"  Status: {info.get('status', 'N/A')}",
            f"  Vector Size: {info.get('vector_size', 'N/A')} dimensions",
            f"  Distance Metric: {info.get('distance', 'N/A')}",
            "",
            "INDEXING STATISTICS:",
            f"  Total Chunks: {stats.get('total_chunks', 0):,}",
            f"  Total Files: {stats.get('total_files', 0):,}",
            f"  Collection Status: {stats.get('collection_status', 'N/A')}",
            "",
            "LANGUAGE DISTRIBUTION:"
        ]

        # Add language breakdown
        languages = stats.get('languages', {})
        if languages:
            sorted_langs = sorted(languages.items(), key=lambda x: x[1], reverse=True)
            for lang, count in sorted_langs:
                percentage = (count / stats.get('total_chunks', 1)) * 100
                output.append(f"  {lang:15s}: {count:6,} chunks ({percentage:5.1f}%)")
        else:
            output.append("  No language data available")

        output.append("")
        output.append("=" * 80)

        result_text = '\n'.join(output)

        # Print to console
        print(result_text)

        # Copy to clipboard
        set_clipboard(result_text)
        logger.info("Statistics copied to clipboard")

        # Show notification
        show_notification(
            "Qdrant Statistics",
            f"📊 {stats.get('total_chunks', 0):,} chunks from {stats.get('total_files', 0):,} files indexed"
        )

        return 0

    except Exception as e:
        logger.error(f"Error getting statistics: {e}", exc_info=True)
        show_notification("Qdrant Statistics Error", str(e))
        return 1


if __name__ == "__main__":
    sys.exit(main())
