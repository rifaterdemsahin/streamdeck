# Qdrant Semantic Search Guide

## Overview

The Qdrant Semantic Search integration provides powerful AI-powered code search capabilities for your Stream Deck automation system. Using vector embeddings and semantic similarity, you can search your entire codebase by meaning rather than just exact text matches.

## Architecture

### Components

1. **Qdrant Vector Database** (`http://localhost:6333`)
   - Stores vector embeddings of code chunks
   - Performs fast similarity searches
   - Persists data locally in `qdrant_storage/`

2. **Ollama Embedding Service** (`http://localhost:11434`)
   - Generates embeddings using `nomic-embed-text:v1.5` model
   - Produces 768-dimensional vectors
   - Runs locally for privacy

3. **QdrantManager Utility** ([5_Symbols/utils/qdrant_manager.py](../5_Symbols/utils/qdrant_manager.py))
   - Python wrapper for Qdrant operations
   - Handles embedding generation
   - Provides search and statistics functions

4. **Stream Deck Scripts**
   - [semantic_search.py](../5_Symbols/scripts/semantic_search.py) - Perform searches
   - [qdrant_stats.py](../5_Symbols/scripts/qdrant_stats.py) - View statistics
   - [check_and_index.py](./check_and_index.py) - Index codebase

## Setup

### Prerequisites

1. **Qdrant Running**
   ```powershell
   # Check if Qdrant is running
   curl http://localhost:6333
   ```

2. **Ollama Installed with Embedding Model**
   ```powershell
   # Install Ollama from https://ollama.ai
   # Pull the embedding model
   ollama pull nomic-embed-text:v1.5
   ```

3. **Python Dependencies**
   ```powershell
   pip install qdrant-client==1.7.3
   ```

### Initial Indexing

Before you can search, you need to index your codebase:

```powershell
# Index the current workspace
cd /path/to/your/project
python check_and_index.py
```

**What gets indexed:**
- Source code files (`.py`, `.js`, `.ts`, `.java`, etc.)
- Documentation files (`.md`, `.txt`, `.rst`)
- Configuration files (`.json`, `.yaml`, `.toml`)
- Shell scripts (`.sh`, `.bash`, `.ps1`)

**What gets excluded:**
- Binary files (`.exe`, `.dll`, `.so`)
- Media files (`.png`, `.jpg`, `.mp4`)
- Dependencies (`node_modules`, `__pycache__`)
- Git metadata (`.git/`)

## Usage

### 1. Semantic Search (Stream Deck Button)

**Setup:**
1. Create new Stream Deck button
2. Set action: `System > Open`
3. Application: `python`
4. Arguments: `C:\path\to\streamdeck\5_Symbols\scripts\semantic_search.py`

**How to use:**
1. Copy your search query to clipboard (e.g., "docker container status check")
2. Press Stream Deck button
3. Results are copied back to clipboard
4. Notification shows number of results found

**Example queries:**
- "How do I check Docker container status?"
- "Git commit and push workflow"
- "AI query integration with OpenAI"
- "Error logging and notification system"
- "Backup and restore Stream Deck configuration"

### 2. View Statistics (Stream Deck Button)

**Setup:**
1. Create new Stream Deck button
2. Set action: `System > Open`
3. Application: `python`
4. Arguments: `C:\path\to\streamdeck\5_Symbols\scripts\qdrant_stats.py`

**Output includes:**
- Total chunks indexed
- Total files indexed
- Language distribution
- Collection health status
- Vector size and distance metric

### 3. Programmatic Usage

```python
from utils.qdrant_manager import QdrantManager

# Initialize manager
manager = QdrantManager()

# Health check
healthy, msg = manager.health_check()
print(f"Status: {healthy} - {msg}")

# Search
results = manager.search(
    query="docker status check",
    limit=5,
    score_threshold=0.5
)

# Format and display
print(manager.format_results(results))

# Get statistics
stats = manager.get_statistics()
print(f"Indexed: {stats['total_chunks']} chunks from {stats['total_files']} files")
```

## Configuration

### QdrantManager Parameters

```python
manager = QdrantManager(
    qdrant_url="http://localhost:6333",      # Qdrant service URL
    ollama_url="http://localhost:11434",     # Ollama service URL
    collection_name="kilocode_codebase",     # Collection name
    embedding_model="nomic-embed-text:v1.5", # Embedding model
    vector_size=768                          # Vector dimensions
)
```

### Search Parameters

```python
results = manager.search(
    query="your search query",          # Natural language query
    limit=5,                             # Max results (default: 5)
    score_threshold=0.5,                 # Min similarity (0-1, default: 0.5)
    file_filter="path/to/file",          # Optional file path filter
    language_filter="py"                 # Optional language filter (py, js, etc.)
)
```

### Indexing Configuration

In [check_and_index.py](./check_and_index.py):

```python
CHUNK_SIZE = 1000      # Characters per chunk
OVERLAP = 200          # Overlap between chunks
VERBOSE = True         # Enable verbose logging
```

## Understanding Results

### SearchResult Object

Each result contains:

```python
@dataclass
class SearchResult:
    content: str          # Code snippet
    file_path: str        # Relative file path
    chunk_index: int      # Chunk number in file
    score: float          # Similarity score (0-1)
    language: str         # Programming language
    metadata: dict        # Additional metadata
```

### Score Interpretation

- **0.8 - 1.0**: Highly relevant, exact semantic match
- **0.6 - 0.8**: Very relevant, strong conceptual match
- **0.4 - 0.6**: Moderately relevant, related concepts
- **0.2 - 0.4**: Loosely related
- **0.0 - 0.2**: Weak connection

## Best Practices

### 1. Query Writing

**Good queries:**
- "How to restart Docker containers"
- "Function that sends notifications to users"
- "Error handling in git operations"
- "Configuration for AI API keys"

**Poor queries:**
- Single words: "docker", "git"
- Too specific: "line 42 in docker_manager.py"
- Code syntax: `def restart_container(name):`

### 2. Regular Re-indexing

Re-index when:
- You add new files
- You make significant code changes
- You start a new project phase

```powershell
# Quick re-index
python check_and_index.py
```

### 3. Performance Optimization

- **Adjust chunk size** for your codebase:
  - Smaller chunks (500-800): Better precision, more results
  - Larger chunks (1000-1500): Better context, fewer results

- **Score threshold tuning**:
  - Lower (0.3-0.4): More results, may include less relevant
  - Higher (0.6-0.8): Fewer results, highly relevant only

### 4. Multi-Device Workflow

- **XL #1**: Use for indexing and statistics (slower operations)
- **XL #2**: Quick searches during video editing
- **Stream Deck +**: Search with rotary dial for score threshold
- **Mobile**: Emergency search when away from desk

## Troubleshooting

### Common Issues

**1. "Cannot connect to Qdrant"**

```powershell
# Check if Qdrant is running
curl http://localhost:6333

# Start Qdrant (if using Docker)
docker start qdrant
```

**2. "Embedding model not found"**

```powershell
# Check installed models
ollama list

# Pull the model
ollama pull nomic-embed-text:v1.5
```

**3. "Collection is empty"**

```powershell
# Index the codebase
cd /path/to/project
python check_and_index.py
```

**4. "No results found"**

- Try a broader query
- Lower the score threshold (0.3-0.4)
- Check if files are actually indexed:
  ```powershell
  python qdrant_stats.py
  ```

**5. Slow search performance**

- Reduce `limit` parameter (try 3-5 results)
- Ensure Qdrant has sufficient resources
- Check network latency to localhost

### Health Checks

```python
from utils.qdrant_manager import QdrantManager

manager = QdrantManager()
healthy, message = manager.health_check()

if not healthy:
    print(f"Issues detected: {message}")
    # Fix services before continuing
```

### Logs

Check logs for detailed error information:

```powershell
# View semantic search logs
Get-Content 6_Semblance\logs\semantic_search.log -Tail 50

# View Qdrant manager logs
Get-Content 6_Semblance\logs\qdrant_manager.log -Tail 50
```

## Advanced Features

### 1. Language-Specific Search

```python
# Search only Python files
results = manager.search(
    query="error handling pattern",
    language_filter="py"
)
```

### 2. File Path Filtering

```python
# Search only in utils directory
results = manager.search(
    query="docker operations",
    file_filter="utils/docker"
)
```

### 3. Custom Collection Management

```python
# Create new collection
manager.create_collection(recreate=True)

# Delete collection
manager.delete_collection()

# Get collection info
info = manager.collection_info()
print(f"Points: {info['points_count']}")
```

### 4. Statistics and Monitoring

```python
stats = manager.get_statistics()

print(f"Total chunks: {stats['total_chunks']}")
print(f"Total files: {stats['total_files']}")
print(f"Languages: {stats['languages']}")
```

## Integration with Existing Tools

### With AI Query Tool

Combine semantic search with AI queries:

1. Search for relevant code: `semantic_search.py`
2. Copy results to clipboard
3. Add context to AI query
4. Run AI query: `ai_query.py`

### With Git Workflow

Find code before making changes:

1. Search for feature: `semantic_search.py`
2. Review found files
3. Make changes
4. Check status: `git_status.py`
5. Commit changes

### With Docker Operations

Find container management code:

1. Search: "docker restart container"
2. Review implementation
3. Check current status: `docker_status.py`
4. Apply operations

## Performance Benchmarks

Typical performance on modern hardware:

| Operation | Time | Notes |
|-----------|------|-------|
| Single search | 100-300ms | Depends on collection size |
| Index 100 files | 2-5 min | With 768-dim embeddings |
| Index 1000 files | 20-40 min | First-time indexing |
| Re-index changed files | 1-10 min | Incremental updates |
| Health check | < 100ms | Quick service validation |
| Get statistics | 200-500ms | Scrolls collection |

## Security and Privacy

### Data Privacy

- **Local-only**: All data stays on your machine
- **No cloud**: Ollama runs locally, no external API calls
- **Persistent storage**: Data in `qdrant_storage/` directory

### Sensitive Information

By default, these are **NOT** indexed:
- `.env` files (API keys, secrets)
- `.git` directory (commit history)
- `node_modules` (dependencies)
- Binary files (executables)

### Backup and Recovery

```powershell
# Backup Qdrant data
Copy-Item -Recurse qdrant_storage qdrant_backup_$(Get-Date -Format "yyyyMMdd_HHmmss")

# Restore from backup
Remove-Item -Recurse qdrant_storage
Copy-Item -Recurse qdrant_backup_TIMESTAMP qdrant_storage
```

## API Reference

### QdrantManager Class

#### Constructor
```python
QdrantManager(
    qdrant_url: str = "http://localhost:6333",
    ollama_url: str = "http://localhost:11434",
    collection_name: str = "kilocode_codebase",
    embedding_model: str = "nomic-embed-text:v1.5",
    vector_size: int = 768
)
```

#### Methods

**health_check() -> Tuple[bool, str]**
- Check if services are running and healthy
- Returns: (is_healthy, message)

**search(query, limit=5, score_threshold=0.5, file_filter=None, language_filter=None) -> List[SearchResult]**
- Perform semantic search
- Returns: List of SearchResult objects

**get_embedding(text) -> List[float]**
- Generate embedding vector for text
- Returns: Vector as list of floats

**collection_info() -> Dict[str, Any]**
- Get collection metadata
- Returns: Dictionary with collection stats

**get_statistics() -> Dict[str, Any]**
- Get indexing statistics
- Returns: Dictionary with stats

**format_results(results, max_content_length=200) -> str**
- Format results for display
- Returns: Formatted string

**create_collection(recreate=False) -> bool**
- Create new collection
- Returns: Success status

**delete_collection() -> bool**
- Delete collection
- Returns: Success status

## Examples

### Example 1: Find Docker-related Code

```python
manager = QdrantManager()

results = manager.search(
    query="how to restart docker containers",
    limit=3,
    language_filter="py"
)

for result in results:
    print(f"\n{result.file_path} (Score: {result.score:.3f})")
    print(result.content[:200])
```

### Example 2: Search with Context

```python
# First search
results = manager.search("git commit workflow")

# Add context and search again
context = " ".join([r.content for r in results[:2]])
detailed_results = manager.search(
    query=f"error handling in: {context}",
    limit=5
)
```

### Example 3: Monitor Indexing Health

```python
stats = manager.get_statistics()

if stats['total_chunks'] < 100:
    print("WARNING: Very few chunks indexed")
    print("Consider running indexing script")

if stats['total_files'] == 0:
    print("ERROR: No files indexed!")
    print("Run: python check_and_index.py")
```

## Future Enhancements

Planned features:

1. **Incremental Indexing**: Only re-index changed files
2. **Multi-Collection Support**: Separate collections per project
3. **Hybrid Search**: Combine semantic + keyword search
4. **Code Similarity**: Find similar code patterns
5. **Search History**: Track and reuse past queries
6. **Auto-Indexing**: Watch filesystem for changes

## Resources

### Documentation
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [Ollama Documentation](https://github.com/ollama/ollama)
- [nomic-embed-text Model](https://www.nomic.ai/blog/posts/nomic-embed-text-v1)

### Related Files
- [qdrant_manager.py](../5_Symbols/utils/qdrant_manager.py) - Utility module
- [semantic_search.py](../5_Symbols/scripts/semantic_search.py) - Search script
- [qdrant_stats.py](../5_Symbols/scripts/qdrant_stats.py) - Statistics script
- [check_and_index.py](./check_and_index.py) - Indexing script
- [test_qdrant_manager.py](../7_Testing_known/unit_tests/test_qdrant_manager.py) - Unit tests

---

**Last Updated:** 2024-02-21

**Status:** Production Ready

**Owner:** Rifat Erdem Sahin
