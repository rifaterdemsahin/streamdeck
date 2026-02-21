#!/usr/bin/env python3
"""
Script Name: restore_streamdeck.py
Purpose: Restore Stream Deck configurations from backup
Author: Rifat Erdem Sahin
Description: Restores Stream Deck profiles and configurations from a backup
"""

import os
import sys
import shutil
import json
from pathlib import Path
import platform

sys.path.append(str(Path(__file__).parent.parent))

from utils.logger import setup_logger
from utils.notification import show_notification

logger = setup_logger('restore_streamdeck')

class StreamDeckRestore:
    """Handle Stream Deck configuration restoration"""

    def __init__(self):
        """Initialize restore manager"""
        self.backup_root = Path(__file__).parent.parent.parent / 'backups'

        # Stream Deck config location on Windows
        if platform.system() == 'Windows':
            self.streamdeck_path = Path(os.getenv('APPDATA')) / 'Elgato' / 'StreamDeck'
        else:
            # For testing on macOS
            self.streamdeck_path = Path.home() / 'Library' / 'Application Support' / 'com.elgato.StreamDeck'

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
                        'name': backup_dir.name,
                        'manifest': manifest
                    })

        # Sort by timestamp
        backups.sort(key=lambda x: x['manifest']['timestamp'], reverse=True)
        return backups

    def restore_from_backup(self, backup_path=None):
        """
        Restore Stream Deck configuration from backup

        Args:
            backup_path: Path to backup folder. If None, uses most recent backup
        """
        try:
            # Find backup to restore
            if backup_path is None:
                backups = self.list_backups()
                if not backups:
                    raise FileNotFoundError("No backups found")
                backup_path = backups[0]['path']
                logger.info(f"Using most recent backup: {backup_path}")
            else:
                backup_path = Path(backup_path)
                if not backup_path.exists():
                    raise FileNotFoundError(f"Backup not found: {backup_path}")

            # Load manifest
            manifest_file = backup_path / 'manifest.json'
            if not manifest_file.exists():
                raise FileNotFoundError("Backup manifest not found")

            with open(manifest_file, 'r') as f:
                manifest = json.load(f)

            logger.info(f"Restoring from backup: {manifest['datetime']}")

            # Create backup of current config before restoring
            if self.streamdeck_path.exists():
                current_backup = self.streamdeck_path.parent / f'StreamDeck_before_restore_{manifest["timestamp"]}'
                logger.info(f"Backing up current config to: {current_backup}")
                shutil.copytree(self.streamdeck_path, current_backup)

            # Ensure target directory exists
            self.streamdeck_path.mkdir(parents=True, exist_ok=True)

            # Restore profiles
            profiles_backup = backup_path / 'ProfilesV2'
            if profiles_backup.exists():
                profiles_target = self.streamdeck_path / 'ProfilesV2'
                if profiles_target.exists():
                    shutil.rmtree(profiles_target)
                shutil.copytree(profiles_backup, profiles_target)
                logger.info("Profiles restored")

            # Restore settings
            settings_backup = backup_path / 'settings.json'
            if settings_backup.exists():
                settings_target = self.streamdeck_path / 'settings.json'
                shutil.copy2(settings_backup, settings_target)
                logger.info("Settings restored")

            # Restore plugins
            plugins_backup = backup_path / 'Plugins'
            if plugins_backup.exists():
                plugins_target = self.streamdeck_path / 'Plugins'
                if plugins_target.exists():
                    shutil.rmtree(plugins_target)
                shutil.copytree(plugins_backup, plugins_target)
                logger.info("Plugins restored")

            logger.info("Restore completed successfully")

            return manifest

        except Exception as e:
            logger.error(f"Restore failed: {e}", exc_info=True)
            raise

    def restore_single_device(self, device_serial, backup_path=None):
        """
        Restore configuration for a single device

        Args:
            device_serial: Serial number of device to restore
            backup_path: Path to backup folder. If None, uses most recent backup
        """
        try:
            # Find backup
            if backup_path is None:
                backups = self.list_backups()
                if not backups:
                    raise FileNotFoundError("No backups found")
                backup_path = backups[0]['path']

            backup_path = Path(backup_path)

            # Find device profile in backup
            device_profile = backup_path / 'ProfilesV2' / device_serial
            if not device_profile.exists():
                raise FileNotFoundError(f"Device {device_serial} not found in backup")

            # Restore device profile
            target_profile = self.streamdeck_path / 'ProfilesV2' / device_serial
            if target_profile.exists():
                shutil.rmtree(target_profile)

            shutil.copytree(device_profile, target_profile)
            logger.info(f"Device {device_serial} restored")

            return True

        except Exception as e:
            logger.error(f"Device restore failed: {e}", exc_info=True)
            raise

def main():
    """Main restore function"""
    try:
        logger.info("Starting Stream Deck restore")

        restore_manager = StreamDeckRestore()

        # Check if specific backup is requested via command line
        backup_path = sys.argv[1] if len(sys.argv) > 1 else None

        if backup_path:
            logger.info(f"Restoring from specified backup: {backup_path}")
        else:
            # List available backups
            backups = restore_manager.list_backups()
            if not backups:
                show_notification("Restore Error", "No backups found")
                logger.error("No backups available")
                return 1

            logger.info(f"Found {len(backups)} backups. Using most recent.")

        # Perform restore
        manifest = restore_manager.restore_from_backup(backup_path)

        # Show summary
        device_count = manifest.get('device_count', 'unknown')
        message = f"Restore completed\nDevices: {device_count}\nFrom: {manifest['datetime']}"
        show_notification("Stream Deck Restore", message)

        logger.info("Please restart Stream Deck software to apply changes")
        logger.info("Restore process completed successfully")

        return 0

    except Exception as e:
        logger.error(f"Restore failed: {e}", exc_info=True)
        show_notification("Restore Error", str(e))
        return 1

if __name__ == "__main__":
    sys.exit(main())
