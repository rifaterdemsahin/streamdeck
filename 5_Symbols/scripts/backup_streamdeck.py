#!/usr/bin/env python3
"""
Script Name: backup_streamdeck.py
Purpose: Backup all Stream Deck configurations
Author: Rifat Erdem Sahin
Description: Creates versioned backup of all Stream Deck profiles and configurations
"""

import os
import sys
import shutil
import json
from pathlib import Path
from datetime import datetime
import platform

sys.path.append(str(Path(__file__).parent.parent))

from utils.logger import setup_logger
from utils.notification import show_notification

logger = setup_logger('backup_streamdeck')

class StreamDeckBackup:
    """Handle Stream Deck configuration backups"""

    def __init__(self):
        """Initialize backup manager"""
        self.backup_root = Path(__file__).parent.parent.parent / 'backups'
        self.backup_root.mkdir(exist_ok=True)

        # Stream Deck config location on Windows
        if platform.system() == 'Windows':
            self.streamdeck_path = Path(os.getenv('APPDATA')) / 'Elgato' / 'StreamDeck'
        else:
            # For testing on macOS
            self.streamdeck_path = Path.home() / 'Library' / 'Application Support' / 'com.elgato.StreamDeck'

    def create_backup(self):
        """Create a new backup of Stream Deck configurations"""
        try:
            # Create timestamp-based backup folder
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_dir = self.backup_root / f'streamdeck_backup_{timestamp}'
            backup_dir.mkdir(parents=True)

            logger.info(f"Creating backup in: {backup_dir}")

            # Check if Stream Deck config exists
            if not self.streamdeck_path.exists():
                raise FileNotFoundError(f"Stream Deck config not found at: {self.streamdeck_path}")

            # Backup profiles
            profiles_path = self.streamdeck_path / 'ProfilesV2'
            if profiles_path.exists():
                shutil.copytree(profiles_path, backup_dir / 'ProfilesV2')
                logger.info("Profiles backed up")

            # Backup settings
            settings_file = self.streamdeck_path / 'settings.json'
            if settings_file.exists():
                shutil.copy2(settings_file, backup_dir / 'settings.json')
                logger.info("Settings backed up")

            # Backup plugin data
            plugins_path = self.streamdeck_path / 'Plugins'
            if plugins_path.exists():
                shutil.copytree(plugins_path, backup_dir / 'Plugins')
                logger.info("Plugins backed up")

            # Create backup manifest
            manifest = {
                'timestamp': timestamp,
                'datetime': datetime.now().isoformat(),
                'source_path': str(self.streamdeck_path),
                'backup_path': str(backup_dir),
                'items_backed_up': {
                    'profiles': profiles_path.exists(),
                    'settings': settings_file.exists(),
                    'plugins': plugins_path.exists()
                },
                'device_count': self._count_devices(backup_dir)
            }

            manifest_file = backup_dir / 'manifest.json'
            with open(manifest_file, 'w') as f:
                json.dump(manifest, f, indent=2)

            logger.info(f"Backup completed: {backup_dir}")

            return backup_dir, manifest

        except Exception as e:
            logger.error(f"Backup failed: {e}", exc_info=True)
            raise

    def _count_devices(self, backup_dir):
        """Count number of devices in backup"""
        profiles_dir = backup_dir / 'ProfilesV2'
        if not profiles_dir.exists():
            return 0

        # Count unique device folders
        device_folders = [d for d in profiles_dir.iterdir() if d.is_dir()]
        return len(device_folders)

    def list_backups(self):
        """List all available backups"""
        backups = []
        for backup_dir in self.backup_root.glob('streamdeck_backup_*'):
            if backup_dir.is_dir():
                manifest_file = backup_dir / 'manifest.json'
                if manifest_file.exists():
                    with open(manifest_file, 'r') as f:
                        manifest = json.load(f)
                    backups.append({
                        'path': backup_dir,
                        'manifest': manifest
                    })

        # Sort by timestamp
        backups.sort(key=lambda x: x['manifest']['timestamp'], reverse=True)
        return backups

    def cleanup_old_backups(self, keep_count=10):
        """Remove old backups, keeping only the most recent"""
        backups = self.list_backups()

        if len(backups) > keep_count:
            for backup in backups[keep_count:]:
                logger.info(f"Removing old backup: {backup['path']}")
                shutil.rmtree(backup['path'])

def main():
    """Main backup function"""
    try:
        logger.info("Starting Stream Deck backup")

        backup_manager = StreamDeckBackup()
        backup_dir, manifest = backup_manager.create_backup()

        # Show summary
        device_count = manifest['device_count']
        message = f"Backup completed\nDevices: {device_count}\nLocation: {backup_dir.name}"
        show_notification("Stream Deck Backup", message)

        # Cleanup old backups
        backup_manager.cleanup_old_backups(keep_count=10)

        logger.info("Backup process completed successfully")
        return 0

    except Exception as e:
        logger.error(f"Backup failed: {e}", exc_info=True)
        show_notification("Backup Error", str(e))
        return 1

if __name__ == "__main__":
    sys.exit(main())
