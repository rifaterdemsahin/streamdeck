# Stream Deck Automation Project - Copilot Instructions

A comprehensive automation system for Stream Deck devices focused on MLOps/DevOps workflows and video editing tasks.

## Project Owner

**Rifat Erdem Sahin**
- Focus: MLOps/DevOps/Video Editing
- Environment: Windows (macOS for development)
- Devices: 2x Stream Deck XL, 1x Stream Deck +, 1x Stream Deck Mobile
- Tools: Python, OpenAI, XAI, OpenRouter, DaVinci Resolve, Slideshow FX plugin, Qdrant (semantic search), Ollama (local embeddings)

## Project Structure

This project follows a **7-folder methodology** for systematic development — from unknown problem to known, validated solution.

### Folder Map

| Folder | Purpose | Key Files |
|--------|---------|-----------|
| [1_Real_Unknown/](1_Real_Unknown/) | Objectives (OKRs) | `objectives.md` |
| [2_Environment/](2_Environment/) | Roadmap & Use Cases | `roadmap.md`, `use-cases.md` |
| [3_Simulation/](3_Simulation/) | UI Examples & Learning Pages | `index.html`, `pages/learning-roadmap.html` |
| [4_Formula/](4_Formula/) | Guides & Best Practices | `setup-guide.md`, `best-practices.md`, `qdrant-semantic-search-guide.md` |
| [5_Symbols/](5_Symbols/) | Core Source Code | `scripts/`, `utils/`, `configs/` |
| [6_Semblance/](6_Semblance/) | Error Logs & Solutions | `error-catalog.md`, `logs/` |
| [7_Testing_known/](7_Testing_known/) | Validation & Tests | `test-plan.md`, `unit_tests/` |

### Source Code Layout

```
5_Symbols/
├── scripts/                        # Stream Deck automation scripts
│   ├── docker_status.py            # Check container statuses
│   ├── git_status.py               # Git operations
│   ├── ai_query.py                 # Multi-model AI queries
│   ├── semantic_search.py          # Qdrant semantic code search
│   ├── qdrant_stats.py             # Qdrant indexing statistics
│   ├── backup_streamdeck.py        # Backup configurations
│   ├── restore_streamdeck.py       # Restore from backup
│   └── learning-assessment.js      # Learning assessment component (Bloom's Taxonomy)
├── utils/                          # Utility modules
│   ├── logger.py                   # Centralized logging
│   ├── docker_manager.py           # Container operations
│   ├── git_manager.py              # Version control operations
│   ├── ai_client.py                # Multi-model AI integration
│   ├── qdrant_manager.py           # Semantic search manager
│   ├── notification.py             # User feedback
│   └── clipboard_manager.py        # Cross-platform clipboard
└── configs/                        # Configuration files
    ├── requirements.txt            # Python dependencies
    ├── .env.example                # Environment variable template
    ├── learning-assessment.html    # Assessment component template
    └── learning-assessment.css     # Assessment component styles
```

## Core Concepts

### 7-Folder Methodology

1. **Real/Unknown** → Define the problem
2. **Environment** → Understand the context
3. **Simulation** → Visualize the solution
4. **Formula** → Plan the implementation
5. **Symbols** → Write the code
6. **Semblance** → Track errors and deviations
7. **Testing/Known** → Validate against objectives

### Script Execution Flow

```
Stream Deck Button Press
    ↓
Python Script (5_Symbols/scripts/)
    ↓
Utility Functions (5_Symbols/utils/)
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

| Component | File | Purpose |
|-----------|------|---------|
| Logger | `utils/logger.py` | Centralized logging to files |
| Docker Manager | `utils/docker_manager.py` | Container operations |
| Git Manager | `utils/git_manager.py` | Version control operations |
| AI Client | `utils/ai_client.py` | Multi-model AI integration |
| Qdrant Manager | `utils/qdrant_manager.py` | Semantic search & vector DB |
| Notification | `utils/notification.py` | User feedback |
| Clipboard Manager | `utils/clipboard_manager.py` | Cross-platform clipboard |

## Semantic Search (Qdrant)

The project includes AI-powered code search using Qdrant vector database and Ollama local embeddings.

### Architecture

- **Qdrant** (`http://localhost:6333`) — Vector database for code chunk embeddings
- **Ollama** (`http://localhost:11434`) — Local embedding generation with `nomic-embed-text:v1.5` (768-dimensional)
- **QdrantManager** (`5_Symbols/utils/qdrant_manager.py`) — Python wrapper for all operations

### Quick Usage

```python
from utils.qdrant_manager import QdrantManager

manager = QdrantManager()

# Health check
healthy, msg = manager.health_check()

# Search by meaning
results = manager.search(
    query="how to restart docker containers",
    limit=5,
    score_threshold=0.5
)

# Get stats
stats = manager.get_statistics()
```

### Indexing

```bash
# Index the codebase
python 4_Formula/check_and_index.py
```

Indexes: `.py`, `.js`, `.ts`, `.java`, `.md`, `.json`, `.yaml`, `.sh` files.
Excludes: binaries, media, `node_modules`, `__pycache__`, `.git/`.

For full details see [Qdrant Semantic Search Guide](4_Formula/qdrant-semantic-search-guide.md).

## Learning System

The project includes a learning assessment system built with Bloom's Taxonomy, plus a master learning roadmap.

### Components

| File | Purpose |
|------|---------|
| `5_Symbols/scripts/learning-assessment.js` | Assessment logic, cookie persistence, roadmap link injection |
| `5_Symbols/configs/learning-assessment.css` | Assessment panel styling |
| `5_Symbols/configs/learning-assessment.html` | Assessment component HTML template |
| `3_Simulation/pages/learning-roadmap.html` | Master roadmap tracking all pages |

### How It Works

- Every learning page in `3_Simulation/pages/` includes the assessment panel
- The panel tracks 5 Bloom's Taxonomy levels: Remember, Understand, Analyze, Evaluate, Create
- Progress is stored in browser cookies (`streamdeck_learning_assessment`)
- `learning-assessment.js` auto-injects a "View Learning Roadmap" link into the panel and the top nav bar
- The roadmap page reads the same cookies to show overall progress across all pages

### Learning Pages

Pages live in `3_Simulation/pages/` and are organized into 5 phases:

1. **Profile Setup** — profile-setup, profile-backout, profile-creator, multi-action, page-jump, pages-setup
2. **Button Config** — colored-buttons, gradient-colors, vertical-horizontal, hotkey-setup, davinci-resolve-icon-pack
3. **DaVinci Resolve** — davinci-profile, edit-point, timeline-markers, timeline-zoom-navigation, dynamic-trim-mode, trim-mode-box-outside, cut-preview-yellow-timeline, cut-page-slidefx, color-grading, video-target-dial, nudge-clip, raise-lower-audio, sound-effects, keyboard-integration, fusion-3d
4. **Stream Deck+ & Hardware** — streamdeck-plus, streamdeck-plus-extension, coarse-fine-dials, knob-click-color-clips, jog-shuttle, 3d-printed-mount, unboxing-experience
5. **Advanced Workflows** — workspace-setup, analog-notes, windows-mover, semantic-search-qdrant

## Multi-Device Setup

| Device | Role |
|--------|------|
| XL #1 | Primary DevOps/MLOps operations |
| XL #2 | Video editing workflows |
| Stream Deck + | AI tools and utilities with rotary controls |
| Mobile | Remote monitoring and emergency operations |

## Quick Start

### Prerequisites

1. Python 3.8+
2. Stream Deck software installed
3. DaVinci Resolve (video editing features)
4. Docker Desktop (DevOps features)
5. Qdrant at `http://localhost:6333` (semantic search)
6. Ollama at `http://localhost:11434` with `nomic-embed-text` model

### Installation

```bash
# Clone the project
cd /path/to/streamdeck

# Set up Python environment
python -m venv streamdeck-env
source streamdeck-env/bin/activate  # macOS/Linux
# .\streamdeck-env\Scripts\activate  # Windows

# Install dependencies
pip install -r 5_Symbols/configs/requirements.txt

# Configure environment variables
cp 5_Symbols/configs/.env.example 5_Symbols/configs/.env
# Edit .env with your API keys

# Test setup
python 5_Symbols/scripts/docker_status.py
```

### Adding New Automation

1. Create script in `5_Symbols/scripts/`:

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

2. Add utility functions to `5_Symbols/utils/` if needed
3. Configure Stream Deck button: `System > Open` → `python` → path to script
4. Add tests to `7_Testing_known/unit_tests/`
5. Document errors in `6_Semblance/error-catalog.md`

## Running Tests

```bash
# Run all unit tests
pytest 7_Testing_known/unit_tests/ -v

# Run specific test
pytest 7_Testing_known/unit_tests/test_docker_manager.py -v

# Run with coverage
pytest 7_Testing_known/unit_tests/ --cov=5_Symbols/utils --cov-report=html
```

## Backup & Recovery

```bash
# Backup all Stream Deck configurations
python 5_Symbols/scripts/backup_streamdeck.py

# Restore most recent backup
python 5_Symbols/scripts/restore_streamdeck.py

# Restore specific backup
python 5_Symbols/scripts/restore_streamdeck.py backups/streamdeck_backup_20240221_143022
```

**Recovery target:** Complete system restore in < 30 minutes.

Backups include: device profiles, button configurations, custom icons, plugin settings, global preferences.

## Troubleshooting

### Quick Checks

1. Is Python in PATH?
2. Is virtual environment activated?
3. Are API keys set in `.env`?
4. Is Docker running?
5. Is Stream Deck software running?
6. Is Qdrant running at `http://localhost:6333`?
7. Is Ollama running at `http://localhost:11434`?

### View Logs

```bash
# View recent logs (macOS/Linux)
tail -50 6_Semblance/logs/docker_status.log

# Windows PowerShell
Get-Content 6_Semblance\logs\docker_status.log -Tail 50
```

### Common Errors

See [6_Semblance/error-catalog.md](6_Semblance/error-catalog.md) for a full catalog.

## Contributing

When making changes:

1. Update relevant documentation in the corresponding folder
2. Add or update tests in `7_Testing_known/`
3. Document any new errors in `6_Semblance/error-catalog.md`
4. Follow patterns in [4_Formula/best-practices.md](4_Formula/best-practices.md)
5. Learning pages should include the assessment component (see `5_Symbols/configs/learning-assessment.html`)

## Resources

### Internal Documentation

- [Setup Guide](4_Formula/setup-guide.md)
- [Best Practices](4_Formula/best-practices.md)
- [Qdrant Semantic Search Guide](4_Formula/qdrant-semantic-search-guide.md)
- [Use Cases](2_Environment/use-cases.md)
- [Test Plan](7_Testing_known/test-plan.md)
- [Error Catalog](6_Semblance/error-catalog.md)
- [Learning Roadmap](3_Simulation/pages/learning-roadmap.html)

### External Links

- [Stream Deck SDK](https://developer.elgato.com/documentation/stream-deck/)
- [DaVinci Resolve Python API](https://www.blackmagicdesign.com/developer/)
- [OpenAI API](https://platform.openai.com/docs)
- [Docker Python SDK](https://docker-py.readthedocs.io/)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [Ollama Documentation](https://github.com/ollama/ollama)

---

**Last Updated:** 2026-02-21

**Project Status:** Development/Setup Phase

**Next Steps:** See [roadmap.md](2_Environment/roadmap.md) for development phases
