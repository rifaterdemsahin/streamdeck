#!/bin/bash

# Kilo Code Setup Script: Ollama and Qdrant Installation
# This script automates the installation and setup of Ollama and Qdrant for Kilo Code

set -e  # Exit on any error

echo "Starting Kilo Code setup..."

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "Homebrew not found. Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Install Python if not available
if ! command -v python3 &> /dev/null; then
    echo "Installing Python..."
    brew install python
fi

# Install pip if not available
if ! command -v pip3 &> /dev/null; then
    echo "Installing pip..."
    python3 -m ensurepip --upgrade
fi

# Install required Python packages
echo "Installing Python dependencies..."
pip3 install qdrant-client requests

# Install Ollama
echo "Installing Ollama..."
brew install ollama

# Start Ollama server in background
echo "Starting Ollama server..."
ollama serve &
OLLAMA_PID=$!
echo "Ollama server started with PID: $OLLAMA_PID"

# Wait a moment for server to start
sleep 5

# Pull coding models
echo "Downloading DeepSeek Coder 6.7B model..."
ollama pull deepseek-coder:6.7b

echo "Downloading DeepSeek Coder 6.7B model..."
ollama pull deepseek-coder:6.7b

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker not found. Installing Docker..."
    brew install --cask docker
    echo "Please start Docker Desktop manually and run this script again."
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "Docker is not running. Please start Docker Desktop and run this script again."
    exit 1
fi

# Create Qdrant storage directory
mkdir -p qdrant_storage

# Start Qdrant
echo "Starting Qdrant..."
docker run -d --name qdrant \
  -p 6333:6333 -p 6334:6334 \
  -v $(pwd)/qdrant_storage:/qdrant/storage \
  qdrant/qdrant

# Wait for Qdrant to start
sleep 10

# Verify installations
echo "Verifying installations..."

# Check Ollama
if curl -s http://localhost:11434/api/tags | grep -q "codellama"; then
    echo "✓ Ollama models downloaded successfully"
else
    echo "✗ Ollama models not found"
fi

# Check Qdrant
if curl -s http://localhost:6333/health | grep -q "Qdrant"; then
    echo "✓ Qdrant is running"
else
    echo "✗ Qdrant is not responding"
fi

echo ""
echo "Setup complete!"
echo "Ollama server is running in background (PID: $OLLAMA_PID)"
echo "Qdrant is running in Docker container"
echo ""
echo "Running component check and codebase indexing..."
python3 4_Formula/check_and_index.py
echo ""
echo "Next steps:"
echo "1. Configure Kilo Code to use Ollama: http://localhost:11434/api/generate"
echo "2. Configure Kilo Code to use Qdrant: http://localhost:6333"
echo "3. Your codebase is now indexed and ready for semantic search"
echo ""
echo "To stop services:"
echo "  kill $OLLAMA_PID  # Stop Ollama"
echo "  docker stop qdrant && docker rm qdrant  # Stop Qdrant"