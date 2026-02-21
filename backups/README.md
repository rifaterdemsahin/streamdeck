# Stream Deck Backups

This directory contains automated backups of all Stream Deck configurations.

## Backup Structure

Each backup is stored in a timestamped folder:
```
streamdeck_backup_YYYYMMDD_HHMMSS/
├── manifest.json           # Backup metadata
├── ProfilesV2/            # Device profiles
├── settings.json          # Global settings
└── Plugins/               # Plugin configurations
```

## Creating a Backup

### Using Stream Deck Button
Press the "Backup Config" button on your Stream Deck

### Using Command Line
```powershell
python 5_Symbols\scripts\backup_streamdeck.py
```

## Restoring from Backup

### Using Stream Deck Button
Press the "Restore Config" button on your Stream Deck

### Using Command Line

Restore most recent backup:
```powershell
python 5_Symbols\scripts\restore_streamdeck.py
```

Restore specific backup:
```powershell
python 5_Symbols\scripts\restore_streamdeck.py backups\streamdeck_backup_20240221_143022
```

## Important Notes

1. **Restart Required:** After restore, restart Stream Deck software
2. **Safety Backup:** Current config is backed up before restore
3. **Retention:** Only last 10 backups are kept automatically
4. **Version Control:** Backups should be committed to git
5. **Manual Backups:** This folder is NOT in .gitignore for disaster recovery

## Backup Schedule

- **Manual:** Before major configuration changes
- **Automated:** Weekly via scheduled task (recommended)
- **Monthly:** Full system test as part of disaster recovery drill

## Manifest File

Each backup includes a manifest.json with:
```json
{
  "timestamp": "20240221_143022",
  "datetime": "2024-02-21T14:30:22",
  "source_path": "C:\\Users\\...\\StreamDeck",
  "backup_path": "..\\backups\\streamdeck_backup_20240221_143022",
  "items_backed_up": {
    "profiles": true,
    "settings": true,
    "plugins": true
  },
  "device_count": 4
}
```

## Troubleshooting

### Backup Fails
- Check Stream Deck software is installed
- Verify Python has read permissions
- Check disk space available

### Restore Fails
- Ensure Stream Deck software is closed
- Check backup manifest.json exists
- Verify backup is not corrupted

### Partial Restore
To restore only one device:
```python
from utils.restore_streamdeck import StreamDeckRestore
restore = StreamDeckRestore()
restore.restore_single_device('DEVICE_SERIAL_NUMBER')
```

## Recovery Time Objective

Target: Complete restore in < 30 minutes

Steps:
1. Install Stream Deck software (10 min)
2. Clone project repository (2 min)
3. Run restore script (5 min)
4. Verify all devices (10 min)
5. Test functionality (3 min)

Total: ~30 minutes
