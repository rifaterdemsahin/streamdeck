# Stream Deck Automation - Setup Guide

## Prerequisites

### Hardware
- 2x Elgato Stream Deck XL (32 keys each)
- 1x Elgato Stream Deck + (8 keys + rotary dials)
- 1x Stream Deck Mobile app (iOS/Android)
- Windows PC with admin access

### Software
- Windows 10/11
- Python 3.8+ installed
- Stream Deck software (latest version)
- DaVinci Resolve
- Slideshow FX plugin for DaVinci Resolve
- Git for Windows
- Docker Desktop (if using containers)
- VS Code or preferred IDE

### API Access
- OpenAI API key
- XAI API access
- OpenRouter account and API key

## Installation Steps

### 1. Install Stream Deck Software

```powershell
# Download from Elgato website
# Install and restart computer
# Connect all Stream Deck devices
```

### 2. Set Up Python Environment

```powershell
# Create virtual environment
python -m venv streamdeck-env

# Activate virtual environment
.\streamdeck-env\Scripts\activate

# Install required packages
pip install streamdeck
pip install openai
pip install requests
pip install python-dotenv
pip install psutil
pip install watchdog
```

### 3. Configure API Keys

Create `.env` file in project root:

```env
OPENAI_API_KEY=your_openai_key_here
XAI_API_KEY=your_xai_key_here
OPENROUTER_API_KEY=your_openrouter_key_here
```

### 4. Install DaVinci Resolve Integration

```powershell
# Install DaVinci Resolve Python API
pip install python-resolve

# Configure Slideshow FX plugin path
# Set environment variable for plugin location
```

### 5. Configure Stream Deck Devices

1. Open Stream Deck software
2. Create new profile: "DevOps-Primary" for XL #1
3. Create new profile: "Video-Editing" for XL #2
4. Create new profile: "AI-Utils" for Stream Deck +
5. Create new profile: "Remote-Monitor" for Mobile

### 6. Set Up Project Structure

```powershell
# Clone or create project directory
cd streamdeck
mkdir scripts
mkdir icons
mkdir configs
mkdir logs
```

## Configuration

### Stream Deck Button Configuration

1. **Open Button Properties**
2. **Set Action Type:** System > Open (for Python scripts)
3. **Command Format:**
   ```
   python C:\path\to\streamdeck\scripts\your_script.py
   ```
4. **Add Custom Icon**
5. **Set Button Title**

### Python Script Template

```python
#!/usr/bin/env python3
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    """Main script function"""
    # Your automation logic here
    pass

if __name__ == "__main__":
    try:
        main()
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
```

### Windows Task Scheduler Integration

For scripts that need elevated permissions:

1. Open Task Scheduler
2. Create new task
3. Set trigger: On demand
4. Action: Run Python script
5. Conditions: Run with highest privileges

## Best Practices

### Script Development
- Use virtual environment for all Python scripts
- Store API keys in `.env` file (never commit to git)
- Add error handling and logging
- Test scripts manually before mapping to buttons
- Use absolute paths in scripts

### Stream Deck Organization
- Group related functions together
- Use consistent color coding
- Clear, readable button labels
- Multi-action buttons for complex workflows
- Folders for organizing large sets of buttons

### Performance
- Cache frequently used data
- Avoid blocking operations in button scripts
- Use background tasks for long operations
- Implement timeout mechanisms
- Monitor resource usage

### Security
- Never store credentials in scripts
- Use environment variables for sensitive data
- Restrict script permissions appropriately
- Regularly update dependencies
- Use HTTPS for all API calls

## Troubleshooting

### Stream Deck Not Detected
1. Reconnect USB cable
2. Try different USB port
3. Restart Stream Deck software
4. Update device firmware

### Python Script Fails
1. Check Python path in button config
2. Verify virtual environment activation
3. Check script permissions
4. Review logs in console
5. Test script from command line first

### API Connection Issues
1. Verify API keys in `.env`
2. Check internet connection
3. Validate API endpoint URLs
4. Review API rate limits
5. Check firewall settings

### DaVinci Resolve Integration
1. Ensure DaVinci Resolve is running
2. Check Python API is enabled in preferences
3. Verify Slideshow FX plugin is installed
4. Check plugin compatibility version
5. Review DaVinci Resolve logs

## Next Steps

1. Complete hardware setup
2. Install all required software
3. Configure API access
4. Test basic button functionality
5. Create first automation script
6. Build out button layouts
7. Test and iterate

Refer to [use-cases.md](../2_Environment/use-cases.md) for implementation examples.
