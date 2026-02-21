# Stream Deck Automation - Best Practices

## Python Script Development

### Script Structure
```python
#!/usr/bin/env python3
"""
Script Name: docker_status.py
Purpose: Check Docker container status
Author: Rifat Erdem Sahin
Created: 2024-01-XX
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/script.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class AutomationScript:
    """Base class for automation scripts"""

    def __init__(self):
        self.setup()

    def setup(self):
        """Initialize script resources"""
        pass

    def execute(self):
        """Main execution logic"""
        raise NotImplementedError

    def cleanup(self):
        """Cleanup resources"""
        pass

    def run(self):
        """Run the script with error handling"""
        try:
            self.execute()
            return 0
        except Exception as e:
            logger.error(f"Script failed: {e}", exc_info=True)
            return 1
        finally:
            self.cleanup()

def main():
    script = AutomationScript()
    return script.run()

if __name__ == "__main__":
    sys.exit(main())
```

### Error Handling
- Always use try-except blocks
- Log errors with context
- Provide user-friendly error messages
- Return appropriate exit codes
- Handle timeout scenarios

### Logging Strategy
- Use Python's logging module
- Log to both file and console
- Include timestamps and log levels
- Rotate log files to prevent bloat
- Different log levels for different environments

## Stream Deck Button Design

### Visual Design
- **Consistency:** Use the same icon style across all buttons
- **Clarity:** Make button purpose obvious at a glance
- **Color Coding:** Consistent colors for similar functions
- **Contrast:** High contrast text and icons
- **Branding:** Optional company/project branding

### Button States
```
Idle State: Blue background, white icon
Active State: Green background, animated icon
Processing: Yellow background, spinner animation
Success: Flash green, return to idle
Error: Red background, exclamation icon
```

### Multi-Action Buttons
Use Stream Deck's multi-action feature for complex workflows:

1. **Sequential Actions:** Execute steps in order
2. **Delays:** Add pauses between actions
3. **Conditional Logic:** Use scripts for branching
4. **Feedback:** Show progress after each step

## API Integration

### Rate Limiting
```python
import time
from functools import wraps

def rate_limit(calls_per_minute):
    """Decorator to limit API calls"""
    min_interval = 60.0 / calls_per_minute
    last_called = [0.0]

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            wait_time = min_interval - elapsed
            if wait_time > 0:
                time.sleep(wait_time)
            result = func(*args, **kwargs)
            last_called[0] = time.time()
            return result
        return wrapper
    return decorator

@rate_limit(calls_per_minute=60)
def call_api(endpoint, data):
    # API call logic
    pass
```

### Caching Responses
```python
import json
from pathlib import Path
from datetime import datetime, timedelta

class APICache:
    def __init__(self, cache_dir='cache', ttl_minutes=5):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.ttl = timedelta(minutes=ttl_minutes)

    def get(self, key):
        cache_file = self.cache_dir / f"{key}.json"
        if cache_file.exists():
            with open(cache_file, 'r') as f:
                data = json.load(f)
                cached_time = datetime.fromisoformat(data['timestamp'])
                if datetime.now() - cached_time < self.ttl:
                    return data['value']
        return None

    def set(self, key, value):
        cache_file = self.cache_dir / f"{key}.json"
        with open(cache_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'value': value
            }, f)
```

### Error Recovery
- Implement retry logic with exponential backoff
- Fallback to cached data when API fails
- Graceful degradation of functionality
- User notification of API issues

## DevOps Automation

### Docker Operations
```python
import docker

class DockerManager:
    def __init__(self):
        self.client = docker.from_env()

    def get_container_status(self):
        containers = self.client.containers.list(all=True)
        return [{
            'name': c.name,
            'status': c.status,
            'image': c.image.tags[0] if c.image.tags else 'unknown'
        } for c in containers]

    def restart_container(self, container_name):
        container = self.client.containers.get(container_name)
        container.restart()
        return True
```

### Git Operations
```python
import subprocess

class GitManager:
    def __init__(self, repo_path):
        self.repo_path = repo_path

    def git_command(self, command):
        result = subprocess.run(
            ['git', '-C', self.repo_path] + command,
            capture_output=True,
            text=True
        )
        return result.stdout, result.stderr, result.returncode

    def status(self):
        stdout, stderr, code = self.git_command(['status', '--short'])
        return stdout

    def quick_commit(self, message):
        self.git_command(['add', '.'])
        self.git_command(['commit', '-m', message])
        return True
```

## Video Editing Automation

### DaVinci Resolve Integration
```python
import DaVinciResolveScript as dvr

class ResolveAutomation:
    def __init__(self):
        self.resolve = dvr.scriptapp("Resolve")
        self.project_manager = self.resolve.GetProjectManager()
        self.project = self.project_manager.GetCurrentProject()

    def create_new_project(self, name):
        return self.project_manager.CreateProject(name)

    def import_media(self, file_paths):
        media_pool = self.project.GetMediaPool()
        return media_pool.ImportMedia(file_paths)

    def export_with_preset(self, preset_name, output_path):
        timeline = self.project.GetCurrentTimeline()
        return self.project.LoadRenderPreset(preset_name)
```

### Slideshow FX Plugin Control
```python
# Windows automation using pyautogui
import pyautogui
import time

class SlideshowFXController:
    def activate_plugin(self):
        # Click Effects Library
        pyautogui.click(x=100, y=200)
        time.sleep(0.5)

        # Type plugin name
        pyautogui.write('Slideshow FX')
        time.sleep(0.3)

        # Press Enter to apply
        pyautogui.press('enter')

    def apply_template(self, template_number):
        # Navigate to template
        # Apply to timeline
        pass
```

## Performance Optimization

### Async Operations
```python
import asyncio
import aiohttp

async def fetch_data(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

async def main():
    urls = ['url1', 'url2', 'url3']
    tasks = [fetch_data(url) for url in urls]
    results = await asyncio.gather(*tasks)
    return results
```

### Background Processing
```python
import threading

def long_running_task():
    # Task that takes time
    pass

def execute_in_background():
    thread = threading.Thread(target=long_running_task)
    thread.daemon = True
    thread.start()
    # Return immediately
    return "Task started in background"
```

## Security Guidelines

### Environment Variables
```python
import os
from dotenv import load_dotenv

load_dotenv()

# Good
API_KEY = os.getenv('OPENAI_API_KEY')

# Bad - never hardcode
# API_KEY = 'sk-1234567890abcdef'
```

### Input Validation
```python
def validate_input(user_input):
    # Sanitize inputs
    if not isinstance(user_input, str):
        raise ValueError("Input must be string")

    # Limit length
    if len(user_input) > 1000:
        raise ValueError("Input too long")

    # Remove dangerous characters
    safe_input = user_input.replace(';', '').replace('&', '')
    return safe_input
```

### Secure API Calls
```python
import requests

def secure_api_call(endpoint, data):
    headers = {
        'Authorization': f"Bearer {os.getenv('API_KEY')}",
        'Content-Type': 'application/json'
    }

    response = requests.post(
        endpoint,
        json=data,
        headers=headers,
        timeout=30,
        verify=True  # Verify SSL certificates
    )

    response.raise_for_status()
    return response.json()
```

## Testing Strategies

### Unit Tests
```python
import unittest

class TestDockerManager(unittest.TestCase):
    def setUp(self):
        self.manager = DockerManager()

    def test_get_container_status(self):
        status = self.manager.get_container_status()
        self.assertIsInstance(status, list)

    def test_restart_container(self):
        result = self.manager.restart_container('test-container')
        self.assertTrue(result)
```

### Integration Tests
- Test complete workflows end-to-end
- Verify button actions produce expected results
- Test error handling scenarios
- Validate API integrations

### Manual Testing Checklist
- [ ] Button responds to press
- [ ] Visual feedback is clear
- [ ] Script executes successfully
- [ ] Error handling works
- [ ] Logging captures events
- [ ] Performance is acceptable
- [ ] No resource leaks

## Maintenance

### Regular Tasks
- Review and update API keys
- Update Python dependencies
- Clean old log files
- Archive unused scripts
- Backup configurations
- Test critical workflows

### Documentation
- Comment complex code sections
- Update README files
- Document API changes
- Keep changelog updated
- Version control all scripts

### Monitoring
- Set up alerts for failures
- Track script execution times
- Monitor API usage and costs
- Review error logs weekly
- Track success/failure rates
