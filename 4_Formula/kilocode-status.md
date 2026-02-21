# Kilo Code Status & Startup Guide

This document provides commands to check the status of Ollama and Qdrant services, and start Kilo Code with codebase indexing for this repository.

## 📊 Status Checks

### Check Ollama Status

```bash
# Check if Ollama service is running
curl -s http://localhost:11434/api/tags | head -10

# List available models
ollama list

# Check specific model (deepseek-coder:6.7b)
ollama list | grep deepseek-coder
```

### Check Qdrant Status

```bash
# Check if Qdrant is running
curl -s http://localhost:6333/health

# Get collection info
curl -s http://localhost:6333/collections/kilocode_codebase

# Check collection stats
curl -s http://localhost:6333/collections/kilocode_codebase | jq '.result.points_count // 0'
```

### Check Kilo Code Configuration

```bash
# Verify configuration file exists
ls -la kilocode.yaml

# Check configuration content
cat kilocode.yaml

# Verify Python dependencies
python3 -c "import qdrant_client, requests; print('✅ Dependencies OK')"
```

## 🚀 Startup Commands

### 1. Start Ollama Service

```bash
# Start Ollama in background (if not already running)
ollama serve &

# Verify it's running
sleep 3
curl -s http://localhost:11434/api/tags | jq '.models | length // 0'
```

### 2. Start Qdrant Database

```bash
# Using Docker (recommended)
docker run -d --name qdrant \
  -p 6333:6333 -p 6334:6334 \
  -v $(pwd)/qdrant_storage:/qdrant/storage \
  qdrant/qdrant

# Or using Docker Compose (if you have docker-compose.yml)
# docker-compose up -d qdrant

# Verify Qdrant is running
sleep 5
curl -s http://localhost:6333/health | jq '.status // "error"'
```

### 3. Download Required Models

```bash
# Download the coding model
ollama pull deepseek-coder:6.7b

# Verify model is downloaded
ollama list | grep deepseek-coder
```

### 4. Index the Codebase

```bash
# Run the indexing script
python3 4_Formula/check_and_index.py

# Or run with custom options
python3 4_Formula/check_and_index.py --verbose
```

### 5. Verify Everything is Working

```bash
# Check all services
echo "=== OLLAMA STATUS ==="
curl -s http://localhost:11434/api/tags | jq '.models[0].name // "No models"'

echo "=== QDRANT STATUS ==="
curl -s http://localhost:6333/health | jq '.status // "error"'

echo "=== COLLECTION STATUS ==="
curl -s http://localhost:6333/collections/kilocode_codebase 2>/dev/null | jq '.result.points_count // 0' || echo "0"

echo "=== PYTHON DEPENDENCIES ==="
python3 -c "import qdrant_client, requests; print('✅ All dependencies available')"
```

## 🔧 Troubleshooting

### Ollama Issues

```bash
# Kill existing Ollama processes
pkill ollama

# Restart Ollama
ollama serve &

# Check logs (if available)
# ollama logs (if supported in your version)
```

### Qdrant Issues

```bash
# Stop and restart Qdrant
docker stop qdrant
docker rm qdrant

# Restart with fresh data
docker run -d --name qdrant \
  -p 6333:6333 -p 6334:6334 \
  -v $(pwd)/qdrant_storage:/qdrant/storage \
  qdrant/qdrant

# Check logs
docker logs qdrant
```

### Indexing Issues

```bash
# Clear existing collection and re-index
python3 -c "
from qdrant_client import QdrantClient
client = QdrantClient('http://localhost:6333')
try:
    client.delete_collection('kilocode_codebase')
    print('✅ Collection cleared')
except:
    print('ℹ️ Collection did not exist')
"

# Re-run indexing
python3 4_Formula/check_and_index.py
```

## 📈 Monitoring Commands

### Real-time Status

```bash
# Watch Ollama status
watch -n 5 'curl -s http://localhost:11434/api/tags | jq ".models | length"'

# Watch Qdrant health
watch -n 5 'curl -s http://localhost:6333/health | jq ".status"'

# Monitor collection growth
watch -n 10 'curl -s http://localhost:6333/collections/kilocode_codebase 2>/dev/null | jq ".result.points_count // 0"'
```

### Performance Metrics

```bash
# Check system resources
echo "=== SYSTEM RESOURCES ==="
echo "CPU: $(top -bn1 | grep 'Cpu(s)' | sed 's/.*, *\([0-9.]*\)%* id.*/\1/' | awk '{print 100 - $1}')%"
echo "Memory: $(free | grep Mem | awk '{printf \"%.0f\", $3/$2 * 100.0}')%"

# Check Docker containers
docker ps | grep -E "(qdrant|ollama)"

# Check running processes
ps aux | grep -E "(ollama|qdrant)" | grep -v grep
```

## 🎯 Quick Start Script

Create and run this script to start everything:

```bash
#!/bin/bash
# kilocode-start.sh - Quick start script for Kilo Code

echo "🚀 Starting Kilo Code services..."

# Start Ollama
echo "📦 Starting Ollama..."
ollama serve > /dev/null 2>&1 &
OLLAMA_PID=$!
sleep 3

# Start Qdrant
echo "🗄️ Starting Qdrant..."
docker run -d --name qdrant \
  -p 6333:6333 -p 6334:6334 \
  -v $(pwd)/qdrant_storage:/qdrant/storage \
  qdrant/qdrant > /dev/null 2>&1
sleep 5

# Download model if needed
echo "🤖 Checking models..."
if ! ollama list | grep -q deepseek-coder; then
    echo "📥 Downloading deepseek-coder:6.7b..."
    ollama pull deepseek-coder:6.7b
fi

# Index codebase
echo "📊 Indexing codebase..."
python3 4_Formula/check_and_index.py

echo "✅ Kilo Code is ready!"
echo "📋 Services running:"
echo "  - Ollama: http://localhost:11434"
echo "  - Qdrant: http://localhost:6333"
echo "  - Collection: kilocode_codebase"
echo ""
echo "🛑 To stop: kill $OLLAMA_PID && docker stop qdrant"
```

## 📋 Status Summary

After running the startup commands, you should see:

```
✅ Ollama: Running with deepseek-coder:6.7b model
✅ Qdrant: Healthy on port 6333
✅ Collection: kilocode_codebase with X indexed chunks
✅ Dependencies: All Python packages available
```

## 🔗 Integration with Kilo Code

Once everything is running, configure Kilo Code with:

- **Model Endpoint**: `http://localhost:11434/api/generate`
- **Model Name**: `deepseek-coder:6.7b`
- **Vector Store**: `http://localhost:6333`
- **Collection**: `kilocode_codebase`

The system is now ready for AI-powered code assistance and semantic search!