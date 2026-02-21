"""
Docker management utility for Stream Deck automation
"""

import docker
from typing import List, Dict

class DockerManager:
    """Manage Docker operations"""

    def __init__(self):
        """Initialize Docker client"""
        self.client = docker.from_env()

    def get_container_status(self) -> List[Dict]:
        """
        Get status of all Docker containers

        Returns:
            List of container information dictionaries
        """
        containers = self.client.containers.list(all=True)
        return [{
            'name': c.name,
            'status': c.status,
            'image': c.image.tags[0] if c.image.tags else 'unknown',
            'id': c.short_id
        } for c in containers]

    def restart_container(self, container_name: str) -> bool:
        """
        Restart a specific container

        Args:
            container_name: Name of the container to restart

        Returns:
            True if successful
        """
        container = self.client.containers.get(container_name)
        container.restart()
        return True

    def stop_all_containers(self) -> int:
        """
        Stop all running containers

        Returns:
            Number of containers stopped
        """
        containers = self.client.containers.list()
        for container in containers:
            container.stop()
        return len(containers)

    def start_container(self, container_name: str) -> bool:
        """
        Start a specific container

        Args:
            container_name: Name of the container to start

        Returns:
            True if successful
        """
        container = self.client.containers.get(container_name)
        container.start()
        return True

    def get_container_logs(self, container_name: str, tail: int = 100) -> str:
        """
        Get logs from a container

        Args:
            container_name: Name of the container
            tail: Number of lines to retrieve (default: 100)

        Returns:
            Container logs as string
        """
        container = self.client.containers.get(container_name)
        logs = container.logs(tail=tail, timestamps=True)
        return logs.decode('utf-8')

    def cleanup_images(self) -> List[str]:
        """
        Remove unused Docker images

        Returns:
            List of removed image IDs
        """
        removed = self.client.images.prune()
        return [img['Deleted'] for img in removed.get('ImagesDeleted', [])]
