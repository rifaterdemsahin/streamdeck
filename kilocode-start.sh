#!/bin/bash
# kilocode-start.sh - Quick start script for Kilo Code
# This script starts all required services and indexes the codebase

set -e  # Exit on any error

echo "🚀 Starting Kilo Code services..."

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "🔍 Checking prerequisites..."

if ! command_exists curl; then
    echo "❌ curl is required but not installed. Please install curl."
    exit 1
fi

if ! command_exists docker; then
    echo "❌ Docker is required but not installed. Please install Docker."
    exit 1
fi

if ! command_exists python3; then
    echo "❌ Python 3 is required but not installed. Please install Python 3."
    exit 1
fi

if ! command_exists ollama; then
    echo "❌ Ollama is required but not installed. Please install Ollama."
    exit 1
fi

# Start Ollama
echo "📦 Starting Ollama..."
if pgrep -f "ollama serve" > /dev/null; then
    echo "ℹ️ Ollama is already running"
else
    ollama serve > /dev/null 2>&1 &
    OLLAMA_PID=$!
    echo "✅ Ollama started with PID: $OLLAMA_PID"
    sleep 3
fi

# Verify Ollama is responding
echo "🔍 Verifying Ollama..."
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "✅ Ollama is responding"
else
    echo "❌ Ollama is not responding. Please check the service."
    exit 1
fi

# Start Qdrant
echo "🗄️ Starting Qdrant..."
if docker ps | grep -q qdrant; then
    echo "ℹ️ Qdrant container is already running"
else
    # Stop any existing stopped containers
    docker stop qdrant > /dev/null 2>&1 || true
    docker rm qdrant > /dev/null 2>&1 || true

    # Start fresh container
    docker run -d --name qdrant \
      -p 6333:6333 -p 6334:6334 \
      -v "$(pwd)/qdrant_storage:/qdrant/storage" \
      qdrant/qdrant > /dev/null 2>&1

    echo "✅ Qdrant container started"
    sleep 5
fi

# Verify Qdrant is responding
echo "🔍 Verifying Qdrant..."
if curl -s http://localhost:6333/health | grep -q '"status":"ok"'; then
    echo "✅ Qdrant is healthy"
else
    echo "❌ Qdrant is not responding. Please check the container."
    exit 1
fi

# Download model if needed
echo "🤖 Checking models..."
if ! ollama list | grep -q "deepseek-coder"; then
    echo "📥 Downloading deepseek-coder:6.7b (this may take a while)..."
    ollama pull deepseek-coder:6.7b
    echo "✅ Model downloaded"
else
    echo "ℹ️ Model deepseek-coder:6.7b is already available"
fi

# Check Python dependencies
echo "🐍 Checking Python dependencies..."
if python3 -c "import qdrant_client, requests" 2>/dev/null; then
    echo "✅ Python dependencies are available"
else
    echo "❌ Python dependencies missing. Installing..."
    pip3 install qdrant-client requests
fi

# Index codebase
echo "📊 Indexing codebase..."
python3 4_Formula/check_and_index.py

echo ""
echo "🎉 Kilo Code is ready!"
echo ""
echo "📋 Services Status:"
echo "  ✅ Ollama: http://localhost:11434"
echo "  ✅ Qdrant: http://localhost:6333"
echo "  ✅ Model: deepseek-coder:6.7b"
echo "  ✅ Collection: kilocode_codebase"
echo ""
echo "🛑 To stop services:"
if [ -n "$OLLAMA_PID" ]; then
    echo "  kill $OLLAMA_PID  # Stop Ollama"
fi
echo "  docker stop qdrant && docker rm qdrant  # Stop Qdrant"
echo ""
echo "💡 Configure Kilo Code with:"
echo "  - Model Endpoint: http://localhost:11434/api/generate"
echo "  - Model Name: deepseek-coder:6.7b"
echo "  - Vector Store: http://localhost:6333"
echo "  - Collection: kilocode_codebase"