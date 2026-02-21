# Kilo Code Setup Guide: Ollama and Qdrant

This document provides step-by-step instructions for setting up Ollama to run local language models for Kilo Code and Qdrant for codebase indexing.

## Prerequisites

- macOS (or Linux/Windows with appropriate package managers)
- Homebrew (for macOS) or equivalent package manager
- Docker (for Qdrant setup)
- Basic command-line knowledge

## Part 1: Setting up Ollama

Ollama allows you to run large language models locally, providing privacy and offline capabilities for Kilo Code.

### 1. Install Ollama

For macOS:
```bash
brew install ollama
```

For other systems, download from the official Ollama website: https://ollama.ai/

### 2. Start the Ollama Server

Open a terminal and run:
```bash
ollama serve
```

This starts the Ollama API server on `http://localhost:11434`. Keep this terminal running in the background.

### 3. Download a Model for Kilo Code

Kilo Code works best with coding-specific models. Pull a suitable model:

```bash
# For general coding assistance
ollama pull deepseek-coder:6.7b

# Alternative models (if available)
# ollama pull codellama:7b
# ollama pull codellama:13b
```

**Note:** The `deepseek-coder:6.7b` model download requires approximately 3.8 GB of disk space and may take several minutes depending on your internet connection. Once downloaded, the model is cached locally and ready for use with Kilo Code's codebase indexing and AI assistance features.

Verify the model is downloaded:
```bash
ollama list
```

### 4. Configure Kilo Code to Use Ollama

In your Kilo Code configuration, set the model endpoint to use Ollama:

- Model API: `http://localhost:11434/api/generate`
- Model Name: `codellama:7b` (or whichever you downloaded)

## Part 2: Setting up Qdrant for Codebase Indexing

Qdrant is a vector database that enables semantic search and indexing of your codebase for better code understanding and retrieval.

### 1. Install Docker

If you don't have Docker installed:

For macOS:
```bash
brew install --cask docker
```

Start Docker Desktop from your Applications folder.

### 2. Run Qdrant

Start a Qdrant instance using Docker:

```bash
docker run -p 6333:6333 -p 6334:6334 \
  -v $(pwd)/qdrant_storage:/qdrant/storage \
  qdrant/qdrant
```

This starts Qdrant on:
- REST API: `http://localhost:6333`
- gRPC API: `http://localhost:6334`
- Data persists in `./qdrant_storage`

### 3. Verify Qdrant is Running

Test the connection:
```bash
curl http://localhost:6333/health
```

You should see: `{"title":"Qdrant","version":"1.7.4"}` (version may vary)

### 4. Configure Kilo Code for Codebase Indexing

In Kilo Code settings:
- Enable codebase indexing
- Set Qdrant endpoint: `http://localhost:6333`
- Configure indexing parameters (collection name, vector dimensions, etc.)

### 5. Index Your Codebase

Use Kilo Code's indexing feature to process your codebase:

1. Open your project in Kilo Code
2. Navigate to Settings > Codebase Indexing
3. Click "Start Indexing"
4. Wait for the process to complete (may take time for large codebases)

## Troubleshooting

### Ollama Issues

- If `ollama serve` fails, ensure no other service is using port 11434
- For GPU acceleration on macOS, Ollama automatically uses Metal
- Check Ollama logs in the terminal where you ran `ollama serve`

### Qdrant Issues

- If Docker container fails to start, ensure Docker Desktop is running
- Check port availability: `lsof -i :6333`
- View Qdrant logs: `docker logs <container_id>`

### Performance Tips

- For better performance, use SSD storage for Qdrant data
- Allocate sufficient RAM to Docker (4GB+ recommended for Qdrant)
- For large codebases, consider using a more powerful machine or cloud instance

## Next Steps

Once both Ollama and Qdrant are set up:
1. Test Kilo Code with a simple coding task
2. Verify that codebase search is working
3. Explore advanced features like multi-file editing and code generation

For more information, refer to:
- Ollama documentation: https://github.com/jmorganca/ollama
- Qdrant documentation: https://qdrant.tech/documentation/
- Kilo Code documentation (if available)