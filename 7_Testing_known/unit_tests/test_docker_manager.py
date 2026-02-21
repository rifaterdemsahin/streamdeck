"""
Unit tests for Docker Manager
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# Add parent directories to path
sys.path.append(str(Path(__file__).parent.parent.parent / '5_Symbols'))

from utils.docker_manager import DockerManager

class TestDockerManager(unittest.TestCase):
    """Test cases for DockerManager class"""

    @patch('docker.from_env')
    def setUp(self, mock_docker):
        """Set up test fixtures"""
        self.mock_client = Mock()
        mock_docker.return_value = self.mock_client
        self.manager = DockerManager()

    def test_init(self):
        """Test DockerManager initialization"""
        self.assertIsNotNone(self.manager.client)

    @patch('docker.from_env')
    def test_get_container_status_empty(self, mock_docker):
        """Test getting status when no containers exist"""
        mock_client = Mock()
        mock_client.containers.list.return_value = []
        mock_docker.return_value = mock_client

        manager = DockerManager()
        status = manager.get_container_status()

        self.assertEqual(status, [])
        mock_client.containers.list.assert_called_once_with(all=True)

    @patch('docker.from_env')
    def test_get_container_status_with_containers(self, mock_docker):
        """Test getting status with containers"""
        # Create mock container
        mock_container = Mock()
        mock_container.name = 'test-nginx'
        mock_container.status = 'running'
        mock_container.short_id = 'abc123'
        mock_container.image.tags = ['nginx:latest']

        mock_client = Mock()
        mock_client.containers.list.return_value = [mock_container]
        mock_docker.return_value = mock_client

        manager = DockerManager()
        status = manager.get_container_status()

        self.assertEqual(len(status), 1)
        self.assertEqual(status[0]['name'], 'test-nginx')
        self.assertEqual(status[0]['status'], 'running')
        self.assertEqual(status[0]['image'], 'nginx:latest')

    @patch('docker.from_env')
    def test_restart_container(self, mock_docker):
        """Test restarting a container"""
        mock_container = Mock()
        mock_client = Mock()
        mock_client.containers.get.return_value = mock_container
        mock_docker.return_value = mock_client

        manager = DockerManager()
        result = manager.restart_container('test-container')

        self.assertTrue(result)
        mock_client.containers.get.assert_called_once_with('test-container')
        mock_container.restart.assert_called_once()

    @patch('docker.from_env')
    def test_stop_all_containers(self, mock_docker):
        """Test stopping all containers"""
        mock_containers = [Mock(), Mock(), Mock()]
        mock_client = Mock()
        mock_client.containers.list.return_value = mock_containers
        mock_docker.return_value = mock_client

        manager = DockerManager()
        count = manager.stop_all_containers()

        self.assertEqual(count, 3)
        for container in mock_containers:
            container.stop.assert_called_once()

    @patch('docker.from_env')
    def test_start_container(self, mock_docker):
        """Test starting a container"""
        mock_container = Mock()
        mock_client = Mock()
        mock_client.containers.get.return_value = mock_container
        mock_docker.return_value = mock_client

        manager = DockerManager()
        result = manager.start_container('test-container')

        self.assertTrue(result)
        mock_container.start.assert_called_once()

    @patch('docker.from_env')
    def test_get_container_logs(self, mock_docker):
        """Test getting container logs"""
        mock_container = Mock()
        mock_container.logs.return_value = b'Test log output'
        mock_client = Mock()
        mock_client.containers.get.return_value = mock_container
        mock_docker.return_value = mock_client

        manager = DockerManager()
        logs = manager.get_container_logs('test-container', tail=50)

        self.assertEqual(logs, 'Test log output')
        mock_container.logs.assert_called_once_with(tail=50, timestamps=True)

if __name__ == '__main__':
    unittest.main()
