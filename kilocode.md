# Kilo Code Integration for Stream Deck Automation

AI-powered code assistance and semantic search integration for the Stream Deck automation project.

## Overview

Kilo Code enhances the Stream Deck automation system by providing:
- Local AI code generation and assistance
- Semantic codebase search and indexing
- Intelligent code understanding and refactoring
- Offline privacy-preserving AI capabilities

## Architecture Integration

### Components Added

- **Ollama:** Local LLM server for running coding models
- **Qdrant:** Vector database for codebase semantic search
- **Codebase Indexer:** Python script that processes and indexes code
- **Kilo Code Client:** Integration with the main automation system

### System Flow

```
User Query → Stream Deck Button
    ↓
Kilo Code Processing
    ↓
Ollama Model (Local)
    ↓
Code Generation/Assistance
    ↓
Qdrant Semantic Search
    ↓
Context-Aware Response
    ↓
Stream Deck Display/Notification
```

## Setup and Installation

### Prerequisites

- macOS (primary development environment)
- Python 3.8+
- Docker Desktop
- 8GB+ RAM recommended
- SSD storage for model files

### Automated Setup

Run the installation script:

```bash
chmod +x 4_Formula/install_kilocode.sh
./4_Formula/install_kilocode.sh
```

This script will:
1. Install Ollama and required models
2. Set up Qdrant vector database
3. Install Python dependencies
4. Index the current codebase
5. Verify all components are working

### Manual Setup

If you prefer manual installation, follow the detailed guide in [4_Formula/formula_kilocode.md](4_Formula/formula_kilocode.md).

## Configuration

### Environment Variables

Add to your `5_Symbols/configs/.env` file:

```bash
# Kilo Code Configuration
OLLAMA_URL=http://localhost:11434
QDRANT_URL=http://localhost:6333
KILOCODE_MODEL=codellama:7b
KILOCODE_COLLECTION=kilocode_codebase
```

### Stream Deck Integration

Create buttons for common Kilo Code operations:

1. **Code Assistant:** Generate code snippets
2. **Semantic Search:** Find related code in codebase
3. **Refactor Code:** Suggest improvements
4. **Index Update:** Refresh codebase index

Example button configuration:
- Action: Run Python script
- Script: `5_Symbols/scripts/kilo_code_assist.py`
- Parameters: `--action generate --query "create docker status function"`

## Usage Examples

### Code Generation

```python
# Button press triggers:
from kilo_code_client import KiloCodeClient

client = KiloCodeClient()
result = client.generate_code("Create a function to check Docker container status")
print(result)
```

### Semantic Search

```python
# Find related code:
results = client.search_codebase("docker status monitoring")
for result in results:
    print(f"File: {result['file_path']}")
    print(f"Content: {result['content'][:200]}...")
```

### Codebase Indexing

```python
# Update index after code changes:
client.index_codebase()
```

## API Reference

### KiloCodeClient Class

```python
class KiloCodeClient:
    def __init__(self, ollama_url: str = "http://localhost:11434",
                 qdrant_url: str = "http://localhost:6333")

    def generate_code(self, prompt: str, context: str = None) -> str
    def search_codebase(self, query: str, limit: int = 5) -> List[Dict]
    def refactor_code(self, code: str, instructions: str) -> str
    def index_codebase(self, path: str = ".") -> bool
    def check_health(self) -> Dict[str, bool]
```

## Integration with Existing Scripts

### Enhancing Docker Manager

```python
# In 5_Symbols/utils/docker_manager.py
from kilo_code_client import KiloCodeClient

class DockerManager:
    def __init__(self):
        self.kilo_client = KiloCodeClient()

    def get_smart_suggestions(self, current_status):
        prompt = f"Analyze Docker status and suggest improvements: {current_status}"
        return self.kilo_client.generate_code(prompt)
```

### AI Query Enhancement

```python
# In 5_Symbols/scripts/ai_query.py
# Add Kilo Code as another AI provider
providers = {
    'openai': OpenAIClient(),
    'kilo_code': KiloCodeClient(),
    'xai': XAIClient()
}
```

## Performance Optimization

### Model Selection

- **deepseek-coder:6.7b** - Specialized for code, fast (default)
- **codellama:7b** - Fast, good for general coding (if available)
- **codellama:13b** - Better quality, slower (if available)

### Indexing Strategy

- Chunk size: 1000 characters with 200 overlap
- Vector dimension: 1536 (matching Kilo Code config)
- Distance metric: Cosine similarity
- Excluded files: binaries, logs, dependencies

### Memory Management

- Models loaded on-demand
- Index cached in Qdrant
- Background processing for large codebases

## Troubleshooting

### Common Issues

1. **Ollama not responding**
   - Check if `ollama serve` is running
   - Verify model is downloaded: `ollama list`

2. **Qdrant connection failed**
   - Ensure Docker container is running: `docker ps`
   - Check port availability: `lsof -i :6333`

3. **Indexing fails**
   - Check file permissions
   - Verify Python dependencies: `pip list | grep qdrant`

4. **Poor code quality**
   - Try different models
   - Provide more context in prompts
   - Use semantic search for examples

### Logs and Debugging

```bash
# View Kilo Code logs
tail -f 6_Semblance/logs/kilo_code.log

# Check Ollama status
curl http://localhost:11434/api/tags

# Check Qdrant health
curl http://localhost:6333/health
```

### Recovery Procedures

1. **Restart services:**
   ```bash
   # Stop existing
   pkill ollama
   docker stop qdrant

   # Restart
   ollama serve &
   docker start qdrant
   ```

2. **Reindex codebase:**
   ```bash
   python 4_Formula/check_and_index.py
   ```

## Development Guidelines

### Adding New Features

1. Create feature branch
2. Add unit tests in `7_Testing_known/unit_tests/`
3. Update documentation
4. Test integration with Stream Deck buttons

### Code Standards

- Follow PEP 8 style guide
- Add type hints for all functions
- Include docstrings with examples
- Handle exceptions gracefully

### Testing

```bash
# Run Kilo Code specific tests
pytest 7_Testing_known/unit_tests/test_kilo_code.py -v

# Test integration
python 4_Formula/check_and_index.py
```

## Security Considerations

- All processing happens locally
- No code sent to external APIs
- Models stored locally
- Index contains only code structure, not sensitive data

## Future Enhancements

- Multi-language model support
- Real-time code analysis
- Integration with version control
- Custom model fine-tuning
- Advanced refactoring suggestions

## Resources

- [Ollama Documentation](https://github.com/jmorganca/ollama)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [Setup Guide](4_Formula/formula_kilocode.md)
- [Error Catalog](6_Semblance/error-catalog.md)

## Support

For Kilo Code specific issues:
1. Check component health: `python -c "from kilo_code_client import KiloCodeClient; print(KiloCodeClient().check_health())"`
2. Review logs in `6_Semblance/logs/`
3. Consult troubleshooting section above

---

**Integration Status:** Active Development

**Last Updated:** 2024-02-21

**Next Steps:** Complete multi-device Stream Deck integration