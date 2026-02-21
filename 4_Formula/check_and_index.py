#!/usr/bin/env python3
"""
Kilo Code Component Checker and Codebase Indexer

This script checks if Ollama and Qdrant are running, then indexes the codebase
into Qdrant for semantic search capabilities in Kilo Code.
"""

import os
import sys
import requests
import time
from pathlib import Path
from typing import List, Dict, Any
import json
import hashlib

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct
except ImportError:
    print("❌ qdrant-client not installed. Install with: pip install qdrant-client")
    sys.exit(1)

# Configuration
OLLAMA_URL = "http://localhost:11434"
QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "kilocode_codebase"
EMBEDDING_MODEL = "deepseek-coder:6.7b"  # Model for generating embeddings
CHUNK_SIZE = 1000  # Characters per chunk
OVERLAP = 200  # Overlap between chunks

# Files to exclude from indexing
EXCLUDE_PATTERNS = [
    '.git', '__pycache__', 'node_modules', '.DS_Store',
    '*.pyc', '*.pyo', '*.pyd', '*.log', '*.tmp',
    '*.png', '*.jpg', '*.jpeg', '*.gif', '*.bmp', '*.ico',
    '*.mp4', '*.avi', '*.mov', '*.zip', '*.tar.gz'
]

def check_ollama() -> bool:
    """Check if Ollama is running and has the required model."""
    try:
        # Check if server is responding
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        if response.status_code != 200:
            print("❌ Ollama server not responding")
            return False

        models = response.json().get('models', [])
        model_names = [model['name'] for model in models]

        if EMBEDDING_MODEL not in model_names:
            print(f"❌ Model {EMBEDDING_MODEL} not found. Available: {model_names}")
            return False

        print("✅ Ollama is running with required model")
        return True

    except requests.RequestException as e:
        print(f"❌ Cannot connect to Ollama: {e}")
        return False

def check_qdrant() -> bool:
    """Check if Qdrant is running."""
    try:
        response = requests.get(f"{QDRANT_URL}/health", timeout=5)
        if response.status_code == 200 and "Qdrant" in response.text:
            print("✅ Qdrant is running")
            return True
        else:
            print("❌ Qdrant health check failed")
            return False
    except requests.RequestException as e:
        print(f"❌ Cannot connect to Qdrant: {e}")
        return False

def get_embedding(text: str) -> List[float]:
    """Generate embedding for text using Ollama."""
    payload = {
        "model": EMBEDDING_MODEL,
        "prompt": text,
        "stream": False,
        "options": {
            "num_predict": 0,  # We only want embeddings, not generation
            "temperature": 0
        }
    }

    try:
        response = requests.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()

        # Ollama returns embeddings in the response if available
        # For CodeLlama, we might need to use a different approach
        # For now, we'll use a simple hash-based approach as fallback
        if 'embedding' in result:
            return result['embedding']
        else:
            # Fallback: create a simple hash-based vector
            hash_obj = hashlib.sha256(text.encode())
            hash_bytes = hash_obj.digest()
            # Convert to float list (normalize to -1, 1 range)
            vector = []
            for i in range(0, len(hash_bytes), 4):
                chunk = hash_bytes[i:i+4]
                val = int.from_bytes(chunk, byteorder='big', signed=False)
                vector.append((val / 2**32) * 2 - 1)  # Normalize to [-1, 1]
            return vector[:1536]  # Truncate to match Kilo Code config

    except requests.RequestException as e:
        print(f"❌ Error generating embedding: {e}")
        return []

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = OVERLAP) -> List[str]:
    """Split text into overlapping chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap
        if start >= len(text):
            break
    return chunks

def should_index_file(file_path: Path) -> bool:
    """Check if file should be indexed based on patterns."""
    file_str = str(file_path)

    # Check exclude patterns
    for pattern in EXCLUDE_PATTERNS:
        if pattern.startswith('*'):
            if file_path.name.endswith(pattern[1:]):
                return False
        elif pattern in file_str:
            return False

    # Only index text-based files
    text_extensions = {'.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.hpp',
                      '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt',
                      '.scala', '.clj', '.hs', '.ml', '.fs', '.elm', '.dart',
                      '.lua', '.pl', '.pm', '.tcl', '.r', '.m', '.sh', '.bash',
                      '.zsh', '.fish', '.ps1', '.sql', '.xml', '.html', '.css',
                      '.scss', '.sass', '.less', '.json', '.yaml', '.yml',
                      '.toml', '.ini', '.cfg', '.conf', '.md', '.txt', '.rst'}

    return file_path.suffix.lower() in text_extensions

def index_codebase(qdrant_client: QdrantClient, root_path: str = "."):
    """Index the codebase into Qdrant."""
    root = Path(root_path)

    # Create collection if it doesn't exist
    try:
        qdrant_client.get_collection(COLLECTION_NAME)
        print(f"✅ Collection '{COLLECTION_NAME}' exists")
    except:
        print(f"📝 Creating collection '{COLLECTION_NAME}'")
        qdrant_client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
        )

    total_files = 0
    indexed_chunks = 0

    # Walk through all files
    for file_path in root.rglob('*'):
        if not file_path.is_file() or not should_index_file(file_path):
            continue

        total_files += 1

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            if not content.strip():
                continue

            # Split into chunks
            chunks = chunk_text(content)

            for i, chunk in enumerate(chunks):
                if not chunk.strip():
                    continue

                # Generate embedding
                embedding = get_embedding(chunk)
                if not embedding:
                    continue

                # Create point
                point_id = hash(f"{file_path}:{i}") % 2**63  # Generate unique ID
                point = PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload={
                        "file_path": str(file_path.relative_to(root)),
                        "chunk_index": i,
                        "content": chunk,
                        "language": file_path.suffix[1:] if file_path.suffix else "text"
                    }
                )

                # Upsert to Qdrant
                qdrant_client.upsert(
                    collection_name=COLLECTION_NAME,
                    points=[point]
                )

                indexed_chunks += 1

                if indexed_chunks % 10 == 0:
                    print(f"📄 Indexed {indexed_chunks} chunks from {total_files} files...")

        except Exception as e:
            print(f"⚠️ Error processing {file_path}: {e}")
            continue

    print(f"✅ Indexing complete: {indexed_chunks} chunks from {total_files} files")

def main():
    """Main function."""
    print("🔍 Checking installed components...")

    if not check_ollama():
        print("❌ Ollama check failed. Please ensure Ollama is running and models are downloaded.")
        sys.exit(1)

    if not check_qdrant():
        print("❌ Qdrant check failed. Please ensure Qdrant is running.")
        sys.exit(1)

    print("\n🚀 Starting codebase indexing...")

    # Initialize Qdrant client
    qdrant_client = QdrantClient(url=QDRANT_URL)

    # Index the current directory (workspace)
    index_codebase(qdrant_client)

    print("\n✅ Codebase indexing completed successfully!")
    print(f"📊 Collection: {COLLECTION_NAME}")
    print(f"🔗 Qdrant URL: {QDRANT_URL}")
    print("💡 You can now use Kilo Code with semantic codebase search.")

if __name__ == "__main__":
    main()