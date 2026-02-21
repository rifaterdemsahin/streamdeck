# Stream Deck Automation - Error Catalog

## Common Errors and Solutions

### Docker Errors

#### Error: Docker daemon not running
**Symptom:**
```
Error: Error while fetching server API version: ('Connection aborted.', FileNotFoundError)
```

**Cause:** Docker Desktop is not running

**Solution:**
1. Start Docker Desktop
2. Wait for Docker to fully initialize
3. Retry the operation

**Prevention:** Create a startup script to ensure Docker is running

---

#### Error: Permission denied accessing Docker socket
**Symptom:**
```
PermissionError: [Errno 13] Permission denied: '/var/run/docker.sock'
```

**Cause:** User doesn't have permission to access Docker

**Solution (Windows):**
1. Add user to docker-users group
2. Restart computer
3. Verify access with `docker ps`

**Solution (Linux/Mac):**
```bash
sudo usermod -aG docker $USER
newgrp docker
```

---

### Git Errors

#### Error: Not a git repository
**Symptom:**
```
fatal: not a git repository (or any of the parent directories): .git
```

**Cause:** Running git commands outside a repository

**Solution:**
1. Check `GIT_REPO_PATH` environment variable
2. Ensure path points to valid git repository
3. Initialize repository if needed: `git init`

---

#### Error: Authentication failed
**Symptom:**
```
fatal: Authentication failed for 'https://github.com/...'
```

**Cause:** Invalid or missing Git credentials

**Solution (Windows):**
1. Use Git Credential Manager
2. Or generate personal access token
3. Configure: `git config credential.helper manager`

---

### AI API Errors

#### Error: Invalid API key
**Symptom:**
```
AuthenticationError: Incorrect API key provided
```

**Cause:** Missing or invalid API key in .env file

**Solution:**
1. Verify API key in .env file
2. Check for extra spaces or quotes
3. Ensure .env file is in correct location
4. Reload environment: `python -c "from dotenv import load_dotenv; load_dotenv()"`

---

#### Error: Rate limit exceeded
**Symptom:**
```
RateLimitError: Rate limit reached for requests
```

**Cause:** Too many API requests in short time

**Solution:**
1. Implement rate limiting in scripts
2. Add delays between requests
3. Use caching for repeated queries
4. Upgrade API plan if needed

**Prevention:** Use the rate_limit decorator from best-practices.md

---

#### Error: Request timeout
**Symptom:**
```
TimeoutError: Request timed out after 30 seconds
```

**Cause:** API taking too long to respond

**Solution:**
1. Increase timeout value in script
2. Check internet connection
3. Reduce prompt complexity
4. Try different AI model

---

### Stream Deck Errors

#### Error: Device not detected
**Symptom:** Stream Deck doesn't appear in Stream Deck software

**Cause:** Connection or driver issue

**Solution:**
1. Reconnect USB cable
2. Try different USB port (use USB 3.0)
3. Restart Stream Deck software
4. Update Stream Deck firmware
5. Reinstall Stream Deck software

---

#### Error: Button action not executing
**Symptom:** Pressing button does nothing

**Cause:** Multiple possible causes

**Solution:**
1. Check button configuration in Stream Deck software
2. Verify Python path is correct
3. Test script manually in terminal
4. Check script permissions
5. Review logs for errors

**Debug Steps:**
```powershell
# Test Python path
python --version

# Test script manually
python C:\path\to\script.py

# Check logs
type ..\6_Semblance\logs\script_name.log
```

---

### Python Environment Errors

#### Error: Module not found
**Symptom:**
```
ModuleNotFoundError: No module named 'docker'
```

**Cause:** Required package not installed

**Solution:**
```powershell
# Activate virtual environment
.\streamdeck-env\Scripts\activate

# Install requirements
pip install -r 5_Symbols/configs/requirements.txt

# Verify installation
pip list
```

---

#### Error: Python not found
**Symptom:**
```
'python' is not recognized as an internal or external command
```

**Cause:** Python not in PATH or not installed

**Solution:**
1. Verify Python installation
2. Add Python to PATH
3. Use full path in Stream Deck button config
4. Restart computer after PATH changes

---

### DaVinci Resolve Errors

#### Error: Cannot connect to DaVinci Resolve
**Symptom:**
```
ConnectionError: Could not connect to DaVinci Resolve
```

**Cause:** DaVinci Resolve not running or API not enabled

**Solution:**
1. Start DaVinci Resolve
2. Enable external scripting:
   - DaVinci Resolve > Preferences > System > General
   - Enable "External scripting using"
   - Select "Network" and set port
3. Restart DaVinci Resolve

---

#### Error: Slideshow FX plugin not found
**Symptom:** Plugin operations fail silently

**Cause:** Plugin path not configured or plugin not installed

**Solution:**
1. Verify plugin installation
2. Check `SLIDESHOW_FX_PLUGIN_PATH` in .env
3. Ensure plugin is compatible with DaVinci Resolve version
4. Reinstall plugin if necessary

---

### Windows-Specific Errors

#### Error: PowerShell execution policy
**Symptom:**
```
Execution policy does not allow running scripts
```

**Cause:** PowerShell script execution disabled

**Solution:**
```powershell
# Run as Administrator
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

#### Error: Windows notification not showing
**Symptom:** No notification appears when script runs

**Cause:** Notifications disabled or Focus Assist enabled

**Solution:**
1. Check notification settings
2. Disable Focus Assist
3. Allow notifications for PowerShell
4. Test with simple notification script

---

## Debugging Tips

### Enable Debug Logging
```python
# In your script
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check Logs
```powershell
# View recent logs
Get-Content ..\6_Semblance\logs\script_name.log -Tail 50
```

### Test Scripts Manually
Always test scripts from command line before adding to Stream Deck:
```powershell
python 5_Symbols\scripts\docker_status.py
```

### Validate Environment
```python
# test_env.py
import os
from dotenv import load_dotenv

load_dotenv()

print("OPENAI_API_KEY:", "Set" if os.getenv('OPENAI_API_KEY') else "Missing")
print("XAI_API_KEY:", "Set" if os.getenv('XAI_API_KEY') else "Missing")
print("OPENROUTER_API_KEY:", "Set" if os.getenv('OPENROUTER_API_KEY') else "Missing")
```

### Monitor Resource Usage
```python
import psutil

print(f"CPU: {psutil.cpu_percent()}%")
print(f"Memory: {psutil.virtual_memory().percent}%")
```

## Getting Help

If you encounter an error not listed here:

1. Check the logs in [6_Semblance/logs/](logs/)
2. Search for similar issues online
3. Review script code for obvious errors
4. Test components individually
5. Document the error and solution in this file
