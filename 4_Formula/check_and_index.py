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
from datetime import datetime

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
EMBEDDING_MODEL = "nomic-embed-text:v1.5"  # Model for generating embeddings
CHUNK_SIZE = 1000  # Characters per chunk
OVERLAP = 200  # Overlap between chunks
VERBOSE = True  # Enable verbose logging

# Files to exclude from indexing
EXCLUDE_PATTERNS = [
    '.git', '__pycache__', 'node_modules', '.DS_Store',
    '*.pyc', '*.pyo', '*.pyd', '*.log', '*.tmp',
    '*.png', '*.jpg', '*.jpeg', '*.gif', '*.bmp', '*.ico',
    '*.mp4', '*.avi', '*.mov', '*.zip', '*.tar.gz'
]

def log_verbose(message: str, level: str = "INFO"):
    """Log verbose messages with timestamp."""
    if VERBOSE:
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        prefix = {
            "INFO": "ℹ️",
            "SUCCESS": "✅",
            "ERROR": "❌",
            "WARNING": "⚠️",
            "PROGRESS": "📊",
            "STAGE": "🔄"
        }.get(level, "•")
        print(f"[{timestamp}] {prefix} {message}")

def check_ollama() -> bool:
    """Check if Ollama is running and has the required model."""
    log_verbose("STAGE 1: Checking Ollama service...", "STAGE")

    try:
        log_verbose(f"Connecting to Ollama at {OLLAMA_URL}...", "INFO")

        # Check if server is responding
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        if response.status_code != 200:
            log_verbose("Ollama server not responding", "ERROR")
            return False

        log_verbose("Ollama server responded successfully", "SUCCESS")

        models = response.json().get('models', [])
        model_names = [model['name'] for model in models]

        log_verbose(f"Found {len(model_names)} models installed", "INFO")
        log_verbose(f"Looking for model: {EMBEDDING_MODEL}", "INFO")

        if EMBEDDING_MODEL not in model_names:
            log_verbose(f"Model {EMBEDDING_MODEL} not found", "ERROR")
            log_verbose(f"Available models: {', '.join(model_names)}", "INFO")
            return False

        log_verbose(f"Model {EMBEDDING_MODEL} found and ready", "SUCCESS")
        return True

    except requests.RequestException as e:
        log_verbose(f"Cannot connect to Ollama: {e}", "ERROR")
        return False

def check_qdrant() -> bool:
    """Check if Qdrant is running."""
    log_verbose("STAGE 2: Checking Qdrant service...", "STAGE")

    try:
        log_verbose(f"Connecting to Qdrant at {QDRANT_URL}...", "INFO")

        response = requests.get(f"{QDRANT_URL}/", timeout=5)
        if response.status_code == 200 and "qdrant" in response.text.lower():
            log_verbose("Qdrant health check passed", "SUCCESS")
            data = response.json()
            version = data.get('version', 'unknown')
            log_verbose(f"Qdrant version: {version}", "INFO")
            return True
        else:
            log_verbose("Qdrant health check failed", "ERROR")
            return False
    except requests.RequestException as e:
        log_verbose(f"Cannot connect to Qdrant: {e}", "ERROR")
        return False

def get_embedding(text: str, show_progress: bool = False) -> List[float]:
    """Generate embedding for text using Ollama."""
    if show_progress:
        log_verbose(f"Generating embedding for {len(text)} characters of text", "INFO")

    # Use the embeddings API endpoint for embedding models
    payload = {
        "model": EMBEDDING_MODEL,
        "prompt": text
    }

    try:
        response = requests.post(f"{OLLAMA_URL}/api/embeddings", json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()

        # Ollama embeddings API returns embeddings in 'embedding' field
        if 'embedding' in result:
            if show_progress:
                log_verbose(f"Embedding generated: {len(result['embedding'])} dimensions", "SUCCESS")
            return result['embedding']
        else:
            if show_progress:
                log_verbose("Using hash-based fallback embedding", "WARNING")
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
        log_verbose(f"Error generating embedding: {e}", "ERROR")
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
    log_verbose("STAGE 4: Preparing codebase indexing...", "STAGE")

    root = Path(root_path)
    log_verbose(f"Root path: {root.absolute()}", "INFO")

    # Create collection if it doesn't exist
    log_verbose("STAGE 4.1: Checking/creating collection...", "STAGE")
    try:
        collection_info = qdrant_client.get_collection(COLLECTION_NAME)
        log_verbose(f"Collection '{COLLECTION_NAME}' already exists", "SUCCESS")
        log_verbose(f"Collection points count: {collection_info.points_count}", "INFO")
    except Exception as e:
        log_verbose(f"Collection does not exist, creating new collection '{COLLECTION_NAME}'", "INFO")
        # nomic-embed-text:v1.5 produces 768-dimensional embeddings
        qdrant_client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=768, distance=Distance.COSINE)
        )
        log_verbose("Collection created successfully", "SUCCESS")

    log_verbose("STAGE 4.2: Scanning files...", "STAGE")

    total_files = 0
    indexed_chunks = 0
    skipped_files = 0
    start_time = time.time()

    # Walk through all files
    all_files = list(root.rglob('*'))
    log_verbose(f"Found {len(all_files)} total items in directory tree", "INFO")

    indexable_files = [f for f in all_files if f.is_file() and should_index_file(f)]
    log_verbose(f"Filtered to {len(indexable_files)} indexable files", "INFO")

    log_verbose("STAGE 4.3: Processing files and generating embeddings...", "STAGE")

    for file_idx, file_path in enumerate(indexable_files, 1):
        total_files += 1

        log_verbose(f"Processing file {file_idx}/{len(indexable_files)}: {file_path.relative_to(root)}", "PROGRESS")

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            if not content.strip():
                log_verbose(f"  Skipping empty file", "WARNING")
                skipped_files += 1
                continue

            # Split into chunks
            chunks = chunk_text(content)
            log_verbose(f"  Split into {len(chunks)} chunks (size: {CHUNK_SIZE}, overlap: {OVERLAP})", "INFO")

            for i, chunk in enumerate(chunks):
                if not chunk.strip():
                    continue

                log_verbose(f"  Processing chunk {i+1}/{len(chunks)}", "INFO")

                # Generate embedding
                embedding = get_embedding(chunk, show_progress=True)
                if not embedding:
                    log_verbose(f"  Failed to generate embedding for chunk {i}", "ERROR")
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
                log_verbose(f"  Upserting chunk {i} to Qdrant (ID: {point_id})", "INFO")
                qdrant_client.upsert(
                    collection_name=COLLECTION_NAME,
                    points=[point]
                )

                indexed_chunks += 1

                if indexed_chunks % 10 == 0:
                    elapsed = time.time() - start_time
                    rate = indexed_chunks / elapsed if elapsed > 0 else 0
                    log_verbose(f"Progress: {indexed_chunks} chunks indexed from {total_files} files ({rate:.1f} chunks/sec)", "PROGRESS")

        except Exception as e:
            log_verbose(f"Error processing {file_path}: {e}", "ERROR")
            skipped_files += 1
            continue

    elapsed_total = time.time() - start_time
    log_verbose("STAGE 4.4: Indexing completed", "STAGE")
    log_verbose(f"Total files processed: {total_files}", "INFO")
    log_verbose(f"Total chunks indexed: {indexed_chunks}", "INFO")
    log_verbose(f"Files skipped: {skipped_files}", "INFO")
    log_verbose(f"Time elapsed: {elapsed_total:.2f} seconds", "INFO")
    log_verbose(f"Average rate: {indexed_chunks/elapsed_total:.1f} chunks/sec", "INFO")

def main():
    """Main function."""
    log_verbose("=" * 80, "INFO")
    log_verbose("KILO CODE CODEBASE INDEXER - Starting", "STAGE")
    log_verbose("=" * 80, "INFO")

    log_verbose("STAGE 0: Pre-flight checks...", "STAGE")

    if not check_ollama():
        log_verbose("Ollama check failed. Please ensure Ollama is running and models are downloaded.", "ERROR")
        sys.exit(1)

    if not check_qdrant():
        log_verbose("Qdrant check failed. Please ensure Qdrant is running.", "ERROR")
        sys.exit(1)

    log_verbose("STAGE 3: Initializing Qdrant client...", "STAGE")
    log_verbose(f"Connecting to Qdrant at {QDRANT_URL}", "INFO")

    # Initialize Qdrant client
    qdrant_client = QdrantClient(url=QDRANT_URL)
    log_verbose("Qdrant client initialized successfully", "SUCCESS")

    # Index the current directory (workspace)
    index_codebase(qdrant_client)

    log_verbose("=" * 80, "INFO")
    log_verbose("INDEXING COMPLETE - Summary", "STAGE")
    log_verbose("=" * 80, "INFO")
    log_verbose(f"Collection: {COLLECTION_NAME}", "INFO")
    log_verbose(f"Qdrant URL: {QDRANT_URL}", "INFO")
    log_verbose("You can now use Kilo Code with semantic codebase search", "SUCCESS")

if __name__ == "__main__":
    main()