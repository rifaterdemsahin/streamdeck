#!/usr/bin/env python3
"""
Script Name: docker_status.py
Purpose: Check Docker container status and display results
Author: Rifat Erdem Sahin
Description: Gets status of all Docker containers for Stream Deck button
"""

import sys
import logging
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from utils.logger import setup_logger
from utils.docker_manager import DockerManager
from utils.notification import show_notification

logger = setup_logger('docker_status')

def main():
    """Get and display Docker container status"""
    try:
        logger.info("Fetching Docker container status")

        docker_mgr = DockerManager()
        containers = docker_mgr.get_container_status()

        if not containers:
            show_notification("Docker Status", "No containers found")
            logger.warning("No Docker containers found")
            return 0

        # Build status message
        running = sum(1 for c in containers if c['status'] == 'running')
        stopped = len(containers) - running

        message = f"Running: {running}\nStopped: {stopped}\nTotal: {len(containers)}"
        show_notification("Docker Status", message)

        # Log details
        for container in containers:
            logger.info(f"{container['name']}: {container['status']}")

        return 0

    except Exception as e:
        logger.error(f"Failed to get Docker status: {e}", exc_info=True)
        show_notification("Docker Error", str(e))
        return 1

if __name__ == "__main__":
    sys.exit(main())
