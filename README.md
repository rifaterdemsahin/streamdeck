# Stream Deck Automation Project

Comprehensive automation system for Stream Deck devices focused on MLOps/DevOps workflows and video editing tasks.

## 🚀 Quick Navigation

| Category | Link | Description |
|----------|------|-------------|
| 🎮 **Visual Guides** | [Open Simulations](3_Simulation/index.html) | Interactive implementation guides with checklists |
| 📖 **Doc Viewer** | [Markdown Renderer](markdown_renderer.html) | Browse all docs with navigation menu |
| 📚 **Documentation** | [Main Docs](claude.md) | Complete project documentation |
| 🌐 **Website** | [GitHub Pages](https://rifaterdemsahin.github.io/streamdeck/) | Live project website |
| 🎯 **Objectives** | [OKRs](1_Real_Unknown/objectives.md) | Project goals and key results |
| 🗺️ **Roadmap** | [Development Plan](2_Environment/roadmap.md) | 7-phase implementation roadmap |
| ⚙️ **Setup** | [Installation Guide](4_Formula/setup-guide.md) | Get started in 15 minutes |
| 💾 **Backup** | [Disaster Recovery](backups/README.md) | Backup and restore system |
| ✅ **Testing** | [Test Plan](7_Testing_known/test-plan.md) | Validation and testing strategy |
| 🔍 **Help** | [Troubleshooting](6_Semblance/error-catalog.md) | Common errors and solutions |

## ⚡ Fast Jumps

**By Task:**

- [🎨 Button Design](3_Simulation/pages/colored-buttons.html) | [🎬 DaVinci Setup](3_Simulation/pages/davinci-profile.html) | [📋 Profile Config](3_Simulation/pages/profile-setup.html)

**By Folder:**

- [1️⃣ Real](1_Real_Unknown/objectives.md) | [2️⃣ Environment](2_Environment/roadmap.md) | [3️⃣ Simulation](3_Simulation/index.html) | [4️⃣ Formula](4_Formula/setup-guide.md) | [5️⃣ Symbols](5_Symbols/scripts/) | [6️⃣ Semblance](6_Semblance/error-catalog.md) | [7️⃣ Testing](7_Testing_known/test-plan.md)

**Quick Actions:**

```powershell
# Backup configurations
python 5_Symbols\scripts\backup_streamdeck.py

# Restore from backup
python 5_Symbols\scripts\restore_streamdeck.py

# Check Docker status
python 5_Symbols\scripts\docker_status.py
```

## 📚 Project Structure (7-Folder Methodology)

This project follows a systematic 7-folder approach from unknown problem to validated solution:

1. **[1_Real_Unknown/](1_Real_Unknown/)** - Problem definition and OKRs
2. **[2_Environment/](2_Environment/)** - Roadmap and use cases
3. **[3_Simulation/](3_Simulation/)** - UI designs and visual guides ⭐ **NEW: Interactive HTML guides**
4. **[4_Formula/](4_Formula/)** - Setup guides and best practices
5. **[5_Symbols/](5_Symbols/)** - Source code and utilities
6. **[6_Semblance/](6_Semblance/)** - Error catalog and logs
7. **[7_Testing_known/](7_Testing_known/)** - Test plans and validation

## 🎮 Interactive Visual Guides

**New!** Interactive HTML simulation system with:
- ✅ **Prerequisites** for each configuration
- ✔️ **Implementation checklists** (progress saved to browser)
- 📝 **Step-by-step guides**
- 💡 **Pro tips and warnings**
- 🔗 **Bidirectional navigation**

[**➡️ Start Here: Open Visual Simulations**](3_Simulation/index.html)

### Available Guides

**Profile Setup:**

- Profile Setup Basics ✅
- Profile Backout System
- Multi-Action Switching
- Page Jump Design

**Button Configuration:**

- Colored Button Organization ✅
- Gradient Colors
- Layout Design
- Hotkey Setup

**DaVinci Resolve:**

- Complete DaVinci Profile ✅
- Timeline & Markers
- Color Grading
- Keyboard Integration

**Advanced Features:**

- Stream Deck+ Knobs
- Workspace Setup
- Multi-Page Config

## 🎯 Project Objectives

### O1: Automate MLOps/DevOps Workflows

- Automate 80% of repetitive tasks
- Reduce execution time by 60%
- Reusable automation scripts

### O2: Streamline Video Editing

- DaVinci Resolve integration
- One-touch operations
- 50% faster setup time

### O3: AI Integration

- OpenAI, XAI, OpenRouter APIs
- Multi-model comparison
- Context-aware automation

### O4: Multi-Device Orchestration

- 2x Stream Deck XL
- 1x Stream Deck +
- 1x Stream Deck Mobile
- Synchronized profiles

### O5: Disaster Recovery

- Automated backup system ✅ **NEW**
- One-click restore
- Version controlled configs
- Monthly recovery drills

## 🛠️ Quick Start

### Prerequisites

- Windows 10/11
- Python 3.8+
- Stream Deck software
- DaVinci Resolve (for video editing)
- Docker Desktop (for DevOps)

### Installation

```powershell
# Set up Python environment
python -m venv streamdeck-env
.\streamdeck-env\Scripts\activate
pip install -r 5_Symbols\configs\requirements.txt

# Configure environment
copy 5_Symbols\configs\.env.example .env
# Edit .env with your API keys
```

### First Steps

1. **Explore Visual Guides:** Open [3_Simulation/index.html](3_Simulation/index.html)
2. **Read Documentation:** [claude.md](claude.md)
3. **Follow Roadmap:** [2_Environment/roadmap.md](2_Environment/roadmap.md)
4. **Test Backup System:** `python 5_Symbols\scripts\backup_streamdeck.py`

## 💾 Backup & Recovery

Create backup:

```powershell
python 5_Symbols\scripts\backup_streamdeck.py
```

Restore from backup:

```powershell
python 5_Symbols\scripts\restore_streamdeck.py
```

**Recovery Time Objective:** < 30 minutes for complete system restore

## 📖 Documentation

- **[claude.md](claude.md)** - Main documentation
- **[3_Simulation/README.md](3_Simulation/README.md)** - Visual guides documentation
- **[1_Real_Unknown/objectives.md](1_Real_Unknown/objectives.md)** - Project OKRs
- **[2_Environment/roadmap.md](2_Environment/roadmap.md)** - Development roadmap
- **[4_Formula/setup-guide.md](4_Formula/setup-guide.md)** - Installation guide
- **[6_Semblance/error-catalog.md](6_Semblance/error-catalog.md)** - Troubleshooting
- **[7_Testing_known/test-plan.md](7_Testing_known/test-plan.md)** - Testing strategy

## 👤 Author

**Rifat Erdem Sahin**

- Focus: MLOps/DevOps/Video Editing
- Environment: Windows
- Devices: 2x Stream Deck XL, 1x Stream Deck +, 1x Stream Deck Mobile

## 📄 License

Personal automation project - 2024
