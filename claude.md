# Stream Deck Automation Project

A comprehensive automation system for Stream Deck devices focused on MLOps/DevOps workflows and video editing tasks.

## Project Owner
**Rifat Erdem Sahin**
- Focus: MLOps/DevOps/Video Editing
- Environment: Windows
- Devices: 2x Stream Deck XL, 1x Stream Deck +, 1x Stream Deck Mobile
- Tools: Python, OpenAI, XAI, OpenRouter, DaVinci Resolve, Slideshow FX plugin, Qdrant (semantic search), Ollama (local embeddings)

## Project Structure

This project follows a 7-folder methodology for systematic development:

### [1_Real_Unknown](1_Real_Unknown/) - Objectives (OKRs)
Defines the unknown problem and project objectives.

**Key Files:**
- [objectives.md](1_Real_Unknown/objectives.md) - Project OKRs and success metrics

**Purpose:** Start with the unknown problem that needs solving - automating repetitive MLOps/DevOps and video editing tasks.

### [2_Environment](2_Environment/) - Roadmap and Use Cases
Contains project roadmap and detailed use cases.

**Key Files:**
- [roadmap.md](2_Environment/roadmap.md) - Development phases and timeline
- [use-cases.md](2_Environment/use-cases.md) - Detailed user scenarios

**Purpose:** Map out the environment and context in which the solution will operate.

### [3_Simulation](3_Simulation/) - UI Examples
User interface designs and button layouts.

**Key Files:**
- [button-layouts.md](3_Simulation/button-layouts.md) - Stream Deck button configurations and visual designs

**Purpose:** Simulate and visualize how the solution will look and feel.

### [4_Formula](4_Formula/) - Guides and Best Practices
Guidelines and best practices for implementation.

**Key Files:**
- [setup-guide.md](4_Formula/setup-guide.md) - Installation and configuration instructions
- [best-practices.md](4_Formula/best-practices.md) - Development best practices and code patterns

**Purpose:** Define the formulas and methodologies for building the solution.

### [5_Symbols](5_Symbols/) - Core Source Code
Main application files and utilities.

**Structure:**
```
5_Symbols/
├── scripts/           # Stream Deck automation scripts
│   ├── docker_status.py
│   ├── git_status.py
│   ├── ai_query.py
│   ├── semantic_search.py      # Semantic code search
│   ├── qdrant_stats.py         # Qdrant statistics
│   ├── backup_streamdeck.py    # Backup configurations
│   └── restore_streamdeck.py   # Restore from backup
├── utils/            # Utility modules
│   ├── logger.py
│   ├── docker_manager.py
│   ├── git_manager.py
│   ├── ai_client.py
│   ├── qdrant_manager.py       # Semantic search manager
│   ├── notification.py
│   └── clipboard_manager.py
└── configs/          # Configuration files
    ├── requirements.txt
    └── .env.example
```

**Purpose:** The actual code symbols that implement the solution.

### [6_Semblance](6_Semblance/) - Error Logs and Solutions
Documents errors, their causes, and solutions.

**Key Files:**
- [error-catalog.md](6_Semblance/error-catalog.md) - Common errors and solutions
- [logs/](6_Semblance/logs/) - Application log files

**Purpose:** Track errors and deviations from expected behavior (semblance of truth vs reality).

### [7_Testing_known](7_Testing_known/) - Validation
Test plans and validation procedures.

**Key Files:**
- [test-plan.md](7_Testing_known/test-plan.md) - Comprehensive test strategy
- [unit_tests/](7_Testing_known/unit_tests/) - Automated unit tests

**Purpose:** Validate the solution against known requirements to reach the objectives.

## Quick Start

### Prerequisites
1. Windows 10/11 (or macOS for development)
2. Python 3.8+
3. Stream Deck software installed
4. DaVinci Resolve (for video editing features)
5. Docker Desktop (for DevOps features)
6. Qdrant (for semantic search) - http://localhost:6333
7. Ollama (for local embeddings) - http://localhost:11434 with nomic-embed-text model

### Installation

1. **Clone/Download Project**
   ```powershell
   cd C:\path\to\streamdeck
   ```

2. **Set Up Python Environment**
   ```powershell
   python -m venv streamdeck-env
   .\streamdeck-env\Scripts\activate
   pip install -r 5_Symbols\configs\requirements.txt
   ```

3. **Configure Environment Variables**
   ```powershell
   copy 5_Symbols\configs\.env.example 5_Symbols\configs\.env
   # Edit .env file with your API keys
   ```

4. **Configure Stream Deck**
   - Open Stream Deck software
   - Create profiles for each device
   - Configure buttons to run Python scripts
   - Example button action: `python C:\path\to\streamdeck\5_Symbols\scripts\docker_status.py`

### First Test

Run a simple test to verify setup:
```powershell
python 5_Symbols\scripts\docker_status.py
```

You should see a notification with Docker container status.

## Usage

### DevOps Workflows
- **Docker Status:** Check all container statuses with one button
- **Git Operations:** Quick commit, push, pull, status checks
- **Log Monitoring:** Real-time log analysis and alerts

### Video Editing Workflows
- **DaVinci Resolve:** Project setup, import, export automation
- **Slideshow FX:** Quick plugin activation and template application

### AI Integration
- **Multi-Model Queries:** Compare responses from OpenAI, XAI, and OpenRouter
- **Code Assistance:** Quick code reviews, explanations, and generation
- **Semantic Search:** AI-powered code search using Qdrant vector database
- **Smart Code Discovery:** Find code by meaning, not just keywords

### Multi-Device Setup
- **XL #1:** Primary DevOps/MLOps operations
- **XL #2:** Video editing workflows
- **Stream Deck +:** AI tools and utilities with rotary controls
- **Mobile:** Remote monitoring and emergency operations

### Semantic Search (Qdrant Skill)

The project includes a powerful semantic search capability powered by Qdrant vector database and Ollama embeddings:

**Key Features:**

- **AI-Powered Search:** Find code by meaning, not just keywords
- **Local & Private:** All embeddings generated locally via Ollama
- **Fast Results:** Sub-second search across entire codebase
- **Multi-Language:** Supports Python, JavaScript, Markdown, and 40+ languages
- **Context-Aware:** Uses 768-dimensional nomic-embed-text embeddings

**Quick Start:**

```powershell
# 1. Ensure services are running
# Qdrant: http://localhost:6333
# Ollama: http://localhost:11434

# 2. Index your codebase
python 4_Formula\check_and_index.py

# 3. Search via clipboard
# Copy: "how to restart docker containers"
# Press: Stream Deck semantic search button
# Results copied to clipboard automatically
```

**Stream Deck Buttons:**

- **Semantic Search:** Copy query → Press button → Get results
- **Qdrant Stats:** View indexing statistics and health

**Learn More:** See [Qdrant Semantic Search Guide](4_Formula/qdrant-semantic-search-guide.md) for detailed documentation.

### Disaster Recovery

- **Backup:** One-click backup of all Stream Deck configurations
- **Restore:** Complete system restore from backup in < 30 minutes
- **Version Control:** All configurations tracked in git
- **Monthly Drills:** Regular testing of recovery procedures

## Development

### Adding New Automation

1. **Create Script in [5_Symbols/scripts/](5_Symbols/scripts/)**
   ```python
   #!/usr/bin/env python3
   import sys
   from pathlib import Path
   sys.path.append(str(Path(__file__).parent.parent))

   from utils.logger import setup_logger

   logger = setup_logger('my_script')

   def main():
       logger.info("Script started")
       # Your automation logic
       return 0

   if __name__ == "__main__":
       sys.exit(main())
   ```

2. **Add Utility Functions to [5_Symbols/utils/](5_Symbols/utils/)** if needed

3. **Configure Stream Deck Button**
   - Set action: System > Open
   - Application: `python`
   - Arguments: `C:\path\to\your_script.py`

4. **Add Tests to [7_Testing_known/](7_Testing_known/)**

5. **Document Errors in [6_Semblance/error-catalog.md](6_Semblance/error-catalog.md)**

### Running Tests

```powershell
# Run all unit tests
pytest 7_Testing_known\unit_tests\ -v

# Run specific test
pytest 7_Testing_known\unit_tests\test_docker_manager.py -v

# Run with coverage
pytest 7_Testing_known\unit_tests\ --cov=5_Symbols\utils --cov-report=html
```

## Architecture

### Script Execution Flow
```
Stream Deck Button Press
    ↓
Python Script Execution
    ↓
Utility Functions (utils/)
    ↓
External API/Service
    ↓
Result Processing
    ↓
Notification to User
    ↓
Logging (6_Semblance/logs/)
```

### Key Components

1. **Logger:** Centralized logging to files
2. **Docker Manager:** Container operations
3. **Git Manager:** Version control operations
4. **AI Client:** Multi-model AI integration
5. **Qdrant Manager:** Semantic search and vector database operations
6. **Notification System:** User feedback
7. **Clipboard Manager:** Cross-platform clipboard operations

## Troubleshooting

Common issues and solutions are documented in [6_Semblance/error-catalog.md](6_Semblance/error-catalog.md)

### Quick Checks
1. Is Python in PATH?
2. Is virtual environment activated?
3. Are API keys set in .env?
4. Is Docker running?
5. Is Stream Deck software running?

### View Logs
```powershell
# View recent logs
Get-Content 6_Semblance\logs\docker_status.log -Tail 50
```

## Project Methodology: 7-Folder System

This project uses the 7-folder methodology:

1. **Real/Unknown** → Define the problem
2. **Environment** → Understand the context
3. **Simulation** → Visualize the solution
4. **Formula** → Plan the implementation
5. **Symbols** → Write the code
6. **Semblance** → Track errors and deviations
7. **Testing/Known** → Validate against objectives

This creates a complete cycle from unknown problem to known, validated solution.

## Contributing

When making changes:
1. Update relevant documentation
2. Add/update tests
3. Document any new errors in error catalog
4. Follow best practices from [4_Formula/best-practices.md](4_Formula/best-practices.md)

## Resources

### Documentation
- [Setup Guide](4_Formula/setup-guide.md)
- [Best Practices](4_Formula/best-practices.md)
- [Qdrant Semantic Search Guide](4_Formula/qdrant-semantic-search-guide.md)
- [Use Cases](2_Environment/use-cases.md)
- [Test Plan](7_Testing_known/test-plan.md)
- [Error Catalog](6_Semblance/error-catalog.md)

### External Links
- [Stream Deck SDK](https://developer.elgato.com/documentation/stream-deck/)
- [DaVinci Resolve Python API](https://www.blackmagicdesign.com/developer/)
- [OpenAI API](https://platform.openai.com/docs)
- [Docker Python SDK](https://docker-py.readthedocs.io/)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [Ollama Documentation](https://github.com/ollama/ollama)

## Backup and Recovery

### Creating Backups

**Using Stream Deck Button:**

- Press "Backup Config" button

**Using Command Line:**

```powershell
python 5_Symbols\scripts\backup_streamdeck.py
```

**What Gets Backed Up:**

- All device profiles (4 devices)
- Button configurations
- Custom icons
- Plugin settings
- Global preferences

### Restoring from Backup

**Using Stream Deck Button:**

- Press "Restore Config" button

**Using Command Line:**

```powershell
# Restore most recent backup
python 5_Symbols\scripts\restore_streamdeck.py

# Restore specific backup
python 5_Symbols\scripts\restore_streamdeck.py backups\streamdeck_backup_20240221_143022
```

**After Restore:**

1. Restart Stream Deck software
2. Verify all devices are recognized
3. Test button functionality

### Backup Location

All backups are stored in [backups/](backups/) directory with timestamps.

See [backups/README.md](backups/README.md) for detailed backup documentation.

### Recovery Time

**Target:** Complete system recovery in < 30 minutes

**Process:**

1. Install Stream Deck software
2. Clone this repository
3. Run restore script
4. Verify functionality

## Version History

### v1.1.0 - Semantic Search Integration

- Qdrant vector database integration
- Semantic code search capability
- Ollama local embeddings (nomic-embed-text)
- QdrantManager utility class
- Semantic search and statistics scripts
- Comprehensive documentation and tests

### v1.0.0 - Initial Setup

- 7-folder structure created
- Core utilities implemented
- Basic Docker, Git, and AI integrations
- Disaster recovery system with backup/restore
- Comprehensive documentation complete

## License

This is a personal automation project for Rifat Erdem Sahin.

## Support

For issues and questions:
1. Check [error-catalog.md](6_Semblance/error-catalog.md)
2. Review logs in [6_Semblance/logs/](6_Semblance/logs/)
3. Consult [best-practices.md](4_Formula/best-practices.md)

---

**Last Updated:** 2024-02-21

**Project Status:** Development/Setup Phase

**Next Steps:** See [roadmap.md](2_Environment/roadmap.md) for development phases
