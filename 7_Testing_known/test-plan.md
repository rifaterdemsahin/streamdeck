# Stream Deck Automation - Test Plan

## Testing Strategy

### 1. Unit Testing (Python Scripts)
Test individual functions and utilities in isolation

### 2. Integration Testing
Test complete workflows from button press to result

### 3. System Testing
Test entire setup with all devices and dependencies

### 4. User Acceptance Testing
Validate against original objectives and use cases

---

## Unit Tests

### Docker Manager Tests
**File:** `test_docker_manager.py`

```python
import unittest
from utils.docker_manager import DockerManager

class TestDockerManager(unittest.TestCase):
    def setUp(self):
        self.manager = DockerManager()

    def test_get_container_status(self):
        """Test getting container status"""
        status = self.manager.get_container_status()
        self.assertIsInstance(status, list)

    def test_container_status_format(self):
        """Test status format is correct"""
        status = self.manager.get_container_status()
        if status:
            container = status[0]
            self.assertIn('name', container)
            self.assertIn('status', container)
            self.assertIn('image', container)
```

**Test Cases:**
- [ ] Get container status returns list
- [ ] Container data has required fields
- [ ] Restart container works
- [ ] Stop all containers works
- [ ] Handle no containers gracefully
- [ ] Handle Docker not running error

---

### Git Manager Tests
**File:** `test_git_manager.py`

**Test Cases:**
- [ ] Get current branch
- [ ] Get status with changes
- [ ] Get status when clean
- [ ] Quick commit works
- [ ] Push to remote
- [ ] Pull from remote
- [ ] Stash and pop changes
- [ ] Handle non-git directory error

---

### AI Client Tests
**File:** `test_ai_client.py`

**Test Cases:**
- [ ] OpenAI query works
- [ ] XAI query works
- [ ] OpenRouter query works
- [ ] Handle invalid API key
- [ ] Handle rate limit error
- [ ] Handle timeout
- [ ] Response format is correct

**Note:** Use mock responses for testing to avoid API costs

---

## Integration Tests

### Test Case IT-001: Docker Status Button
**Objective:** Verify Docker status button shows correct information

**Prerequisites:**
- Docker Desktop running
- At least 2 containers (1 running, 1 stopped)
- Stream Deck connected

**Steps:**
1. Press "Docker Status" button on Stream Deck
2. Observe notification

**Expected Result:**
- Notification appears within 2 seconds
- Shows correct count of running containers
- Shows correct count of stopped containers
- Shows total container count

**Validation Criteria:**
- [ ] Notification appears
- [ ] Counts are accurate
- [ ] No error messages
- [ ] Log file created

---

### Test Case IT-002: Git Quick Commit
**Objective:** Verify git commit workflow

**Prerequisites:**
- Git repository with uncommitted changes
- Git configured with user name and email

**Steps:**
1. Make changes to a file
2. Press "Quick Commit" button
3. Check git log

**Expected Result:**
- Changes are committed
- Commit message includes timestamp
- Notification confirms success

**Validation Criteria:**
- [ ] Commit appears in git log
- [ ] All changes included
- [ ] Commit message formatted correctly
- [ ] Notification shown

---

### Test Case IT-003: AI Query
**Objective:** Test AI integration

**Prerequisites:**
- Valid API key in .env
- Text in clipboard

**Steps:**
1. Copy "What is Docker?" to clipboard
2. Press "Ask OpenAI" button
3. Wait for response
4. Check clipboard

**Expected Result:**
- Response appears in clipboard
- Notification shows completion
- Response is relevant to query

**Validation Criteria:**
- [ ] Response received
- [ ] Response copied to clipboard
- [ ] Notification displayed
- [ ] Log shows API call

---

### Test Case IT-004: Multi-Device Workflow
**Objective:** Test switching between Stream Deck devices

**Prerequisites:**
- All 4 Stream Deck devices connected
- Different profiles configured for each

**Steps:**
1. Use Stream Deck XL #1 for Docker operation
2. Switch to Stream Deck XL #2 for video editing
3. Use Stream Deck + for AI query
4. Check status on Stream Deck Mobile

**Expected Result:**
- Each device executes correct scripts
- No conflicts between devices
- All operations succeed

**Validation Criteria:**
- [ ] All devices respond
- [ ] Correct scripts execute
- [ ] No cross-device interference

---

## System Tests

### Test Case ST-001: Complete DevOps Workflow
**Objective:** Test full DevOps automation workflow

**Scenario:**
1. Check Docker status
2. Check Git status
3. Make code changes
4. Quick commit changes
5. Run tests (simulated)
6. Deploy to staging (simulated)

**Validation Criteria:**
- [ ] All steps complete successfully
- [ ] Appropriate notifications shown
- [ ] Logs captured for all operations
- [ ] No errors occur

---

### Test Case ST-002: Video Editing Workflow
**Objective:** Test DaVinci Resolve integration

**Prerequisites:**
- DaVinci Resolve installed and running
- Slideshow FX plugin installed

**Scenario:**
1. Create new project via Stream Deck
2. Import media files
3. Activate Slideshow FX plugin
4. Apply effect template
5. Export with preset

**Validation Criteria:**
- [ ] Project created
- [ ] Media imported
- [ ] Plugin activated
- [ ] Effects applied
- [ ] Export initiated

---

### Test Case ST-003: Error Recovery
**Objective:** Test error handling and recovery

**Scenarios:**
1. Docker not running - Press Docker status button
2. Invalid Git repo - Press Git status button
3. No internet - Press AI query button
4. Invalid API key - Press AI query button

**Validation Criteria:**
- [ ] Appropriate error messages shown
- [ ] Scripts don't crash
- [ ] Errors logged
- [ ] User notified of issue

---

## Performance Tests

### Test Case PT-001: Response Time
**Objective:** Measure button response times

**Metrics:**
- Docker Status: < 2 seconds
- Git Status: < 1 second
- AI Query: < 30 seconds
- DaVinci operation: < 5 seconds

**Validation Criteria:**
- [ ] All operations meet time requirements
- [ ] No degradation over time
- [ ] Consistent performance

---

### Test Case PT-002: Resource Usage
**Objective:** Monitor system resource usage

**Metrics:**
- CPU usage < 10% when idle
- Memory usage < 500MB total
- No memory leaks
- Proper cleanup after operations

**Validation Criteria:**
- [ ] Resources within limits
- [ ] No memory leaks
- [ ] CPU returns to normal after operation

---

## User Acceptance Tests

### UAT-001: OKR Validation
**Objective:** Validate against objectives from [1_Real_Unknown/objectives.md](../1_Real_Unknown/objectives.md)

**Test Against Each Key Result:**

**KR1.1: Automate 80% of repetitive DevOps tasks**
- [ ] List top 10 repetitive tasks
- [ ] Count how many are automated
- [ ] Calculate percentage

**KR1.2: Reduce task execution time by 60%**
- [ ] Measure time before automation
- [ ] Measure time after automation
- [ ] Calculate time savings

**KR2.1: DaVinci Resolve integration**
- [ ] One-touch operations work
- [ ] All common tasks covered

**KR3.1: AI Integration**
- [ ] OpenAI works
- [ ] XAI works
- [ ] OpenRouter works

**KR4.1-4.4: Multi-device setup**
- [ ] All devices configured
- [ ] Profiles assigned correctly
- [ ] Synchronized operation

**KR5.1-5.5: Disaster Recovery**

- [ ] Backup system created
- [ ] Restore functionality works
- [ ] Recovery procedures documented
- [ ] Monthly testing process established
- [ ] All configurations in version control

---

## Disaster Recovery Tests

### Test Case DR-001: Configuration Backup

**Objective:** Verify backup system captures all configurations

**Prerequisites:**

- All Stream Deck devices configured
- Backup script installed

**Steps:**

1. Run backup script
2. Verify backup file created
3. Check backup contains all profiles
4. Verify backup includes button configurations
5. Confirm backup has timestamps

**Expected Result:**

- Backup file created successfully
- All device configurations included
- Backup file is properly formatted
- Timestamp indicates current backup

**Validation Criteria:**

- [ ] Backup file exists
- [ ] All 4 devices included
- [ ] All profiles captured
- [ ] File size reasonable
- [ ] No errors in log

---

### Test Case DR-002: Complete System Restore

**Objective:** Verify restore from backup works completely

**Prerequisites:**

- Valid backup file exists
- Fresh Stream Deck software installation
- All devices connected

**Steps:**

1. Clear all existing Stream Deck configurations
2. Run restore script with backup file
3. Verify profiles loaded on all devices
4. Test button functionality on each device
5. Verify scripts and paths are correct

**Expected Result:**

- All profiles restored correctly
- All buttons functional
- No missing configurations
- All 4 devices working

**Validation Criteria:**

- [ ] Restore completes without errors
- [ ] All profiles appear in Stream Deck software
- [ ] Buttons execute correct scripts
- [ ] Icons display correctly
- [ ] Device-specific settings preserved

---

### Test Case DR-003: Partial Device Restore

**Objective:** Restore configuration for single device

**Prerequisites:**

- Backup file exists
- Single device needs restoration

**Steps:**

1. Run restore script with device filter
2. Verify only selected device is restored
3. Test that other devices are unaffected
4. Validate restored device functionality

**Expected Result:**

- Only specified device restored
- Other devices unchanged
- Restored device fully functional

**Validation Criteria:**

- [ ] Selective restore works
- [ ] No side effects on other devices
- [ ] Restored device matches backup

---

### Test Case DR-004: Backup Version Control

**Objective:** Verify backups are version controlled

**Prerequisites:**

- Git repository initialized
- Backup script configured

**Steps:**

1. Create initial backup
2. Make configuration changes
3. Create second backup
4. Check git history
5. Restore from older version

**Expected Result:**

- Each backup committed to git
- Can view backup history
- Can restore from any version
- Commit messages include timestamps

**Validation Criteria:**

- [ ] Backups in git history
- [ ] Meaningful commit messages
- [ ] Can diff between versions
- [ ] Restore from old backup works

---

### Test Case DR-005: Recovery Time Objective

**Objective:** Measure time to restore from disaster

**Scenario:** Complete system failure - all Stream Deck configurations lost

**Steps:**

1. Start timer
2. Install Stream Deck software
3. Clone backup repository
4. Run restore script
5. Verify all devices functional
6. Stop timer

**Target:** Complete recovery in < 30 minutes

**Validation Criteria:**

- [ ] Recovery time under 30 minutes
- [ ] Process documented
- [ ] No manual intervention needed
- [ ] All functionality restored

---

## Regression Tests

Run these tests before any release or major change:

1. [ ] All unit tests pass
2. [ ] All integration tests pass
3. [ ] All system tests pass
4. [ ] No new errors in logs
5. [ ] Performance within acceptable range
6. [ ] All Stream Deck devices working
7. [ ] All API integrations working

---

## Test Execution Log

### Test Run: [Date]

**Tester:** Rifat Erdem Sahin

**Environment:**
- Windows Version:
- Python Version:
- Stream Deck Software Version:
- DaVinci Resolve Version:

**Results:**
| Test ID | Status | Notes |
|---------|--------|-------|
| IT-001  | ⬜ PASS / ⬜ FAIL | |
| IT-002  | ⬜ PASS / ⬜ FAIL | |
| IT-003  | ⬜ PASS / ⬜ FAIL | |
| IT-004  | ⬜ PASS / ⬜ FAIL | |
| ST-001  | ⬜ PASS / ⬜ FAIL | |
| ST-002  | ⬜ PASS / ⬜ FAIL | |
| ST-003  | ⬜ PASS / ⬜ FAIL | |
| PT-001  | ⬜ PASS / ⬜ FAIL | |
| PT-002  | ⬜ PASS / ⬜ FAIL | |

**Overall Status:** ⬜ PASS / ⬜ FAIL

**Issues Found:**

**Notes:**

---

## Continuous Testing

### Automated Tests
Run unit tests automatically:
```powershell
# In project root
pytest 7_Testing_known/unit_tests/ -v
```

### Daily Checks
- [ ] Run smoke tests
- [ ] Check error logs
- [ ] Verify API connectivity
- [ ] Test critical workflows

### Weekly Validation
- [ ] Full integration test suite
- [ ] Performance benchmarks
- [ ] Resource usage monitoring
- [ ] Update test results

---

## Test Data

### Sample Docker Containers
Create test containers:
```bash
docker run -d --name test-nginx nginx
docker run -d --name test-redis redis
docker create --name test-stopped alpine
```

### Sample Git Repository
```bash
mkdir test-repo
cd test-repo
git init
echo "test" > README.md
git add README.md
git commit -m "Initial commit"
```

### Sample AI Prompts
- "Explain Docker in one sentence"
- "What is Git?"
- "Write a Python function to add two numbers"

---

## Success Criteria

Project is ready for production when:
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] All OKRs validated
- [ ] No critical bugs
- [ ] Performance meets requirements
- [ ] Documentation complete
- [ ] User can execute all planned workflows
