# Qdrant Database Inspection & Repository Status

This document provides commands and scripts to inspect Qdrant database contents and check the indexing status of the repository.

## 🔍 Qdrant Database Inspection

### Basic Status Checks

```bash
# Check if Qdrant is running
docker ps | grep qdrant

# Get container logs
docker logs qdrant

# Check health (different endpoints)
curl -s http://localhost:6333/healthz || echo "healthz failed"
curl -s http://localhost:6333/readyz || echo "readyz failed"
curl -s http://localhost:6333/livez || echo "livez failed"

# Get server info
curl -s http://localhost:6333/ | jq '.'
```

### Collection Inspection

```bash
# List all collections
curl -s http://localhost:6333/collections | jq '.result.collections[]?.name'

# Get detailed collection info
curl -s http://localhost:6333/collections/kilocode_codebase | jq '.'

# Check collection points count
curl -s http://localhost:6333/collections/kilocode_codebase | jq '.result.points_count // 0'

# Get collection configuration
curl -s http://localhost:6333/collections/kilocode_codebase | jq '.result.config'
```

### Data Sampling

```bash
# Get sample points (first 5)
curl -X POST http://localhost:6333/collections/kilocode_codebase/points/scroll \
  -H "Content-Type: application/json" \
  -d '{"limit": 5, "with_payload": true, "with_vector": false}' | jq '.'

# Search for similar vectors (test query)
curl -X POST http://localhost:6333/collections/kilocode_codebase/points/search \
  -H "Content-Type: application/json" \
  -d '{
    "vector": [0.1, 0.1, 0.1],
    "limit": 3,
    "with_payload": true
  }' | jq '.'
```

## 📊 Repository Indexing Status

### File Count Analysis

```bash
# Count total files in repository
find . -type f | wc -l

# Count code files (Python, JS, HTML, etc.)
find . -type f \( -name "*.py" -o -name "*.js" -o -name "*.html" -o -name "*.css" -o -name "*.md" \) | wc -l

# Count files by type
echo "=== FILE TYPE BREAKDOWN ==="
find . -type f -name "*.py" | wc -l | xargs echo "Python files:"
find . -type f -name "*.js" | wc -l | xargs echo "JavaScript files:"
find . -type f -name "*.html" | wc -l | xargs echo "HTML files:"
find . -type f -name "*.css" | wc -l | xargs echo "CSS files:"
find . -type f -name "*.md" | wc -l | xargs echo "Markdown files:"
find . -type f -name "*.sh" | wc -l | xargs echo "Shell scripts:"
```

### Indexing Coverage Check

```bash
# Check if indexing script exists
ls -la 4_Formula/check_and_index.py

# Check Python dependencies
python3 -c "import qdrant_client, requests; print('✅ Dependencies OK')" 2>/dev/null || echo "❌ Dependencies missing"

# Check configuration
ls -la kilocode.yaml
cat kilocode.yaml | grep -E "(collection|model|dimension)"
```

## 🔧 Automated Inspection Script

```bash
#!/bin/bash
# qdrant-inspection.sh - Comprehensive Qdrant and repository status check

echo "🔍 QDRANT DATABASE & REPOSITORY INSPECTION"
echo "=========================================="
echo ""

# Function to check command success
check_cmd() {
    if eval "$1" > /dev/null 2>&1; then
        echo "✅ $2"
        return 0
    else
        echo "❌ $2"
        return 1
    fi
}

echo "=== DOCKER CONTAINER STATUS ==="
docker ps | grep -q qdrant && echo "✅ Qdrant container is running" || echo "❌ Qdrant container not found"

echo ""
echo "=== QDRANT SERVICE HEALTH ==="
if curl -s http://localhost:6333/ > /dev/null 2>&1; then
    echo "✅ Qdrant service is responding"

    # Get version info
    VERSION=$(curl -s http://localhost:6333/ | jq -r '.version // "unknown"')
    echo "📦 Qdrant version: $VERSION"
else
    echo "❌ Qdrant service not responding"
fi

echo ""
echo "=== COLLECTIONS STATUS ==="
if curl -s http://localhost:6333/collections > /dev/null 2>&1; then
    COLLECTIONS=$(curl -s http://localhost:6333/collections | jq -r '.result.collections[]?.name' 2>/dev/null || echo "")
    if [ -n "$COLLECTIONS" ]; then
        echo "📚 Collections found:"
        echo "$COLLECTIONS" | while read -r collection; do
            echo "  - $collection"

            # Get points count for each collection
            POINTS=$(curl -s "http://localhost:6333/collections/$collection" | jq -r '.result.points_count // 0' 2>/dev/null || echo "0")
            echo "    Points: $POINTS"
        done
    else
        echo "📚 No collections found"
    fi
else
    echo "❌ Cannot access collections endpoint"
fi

echo ""
echo "=== REPOSITORY STATISTICS ==="
TOTAL_FILES=$(find . -type f | wc -l)
CODE_FILES=$(find . -type f \( -name "*.py" -o -name "*.js" -o -name "*.html" -o -name "*.css" -o -name "*.md" -o -name "*.sh" \) | wc -l)
INDEXABLE_FILES=$(find . -type f \( -name "*.py" -o -name "*.js" -o -name "*.html" -o -name "*.css" -o -name "*.md" \) | wc -l)

echo "📁 Total files: $TOTAL_FILES"
echo "💻 Code files: $CODE_FILES"
echo "🔍 Indexable files: $INDEXABLE_FILES"

echo ""
echo "=== INDEXING STATUS ==="
if [ -f "4_Formula/check_and_index.py" ]; then
    echo "✅ Indexing script exists"
else
    echo "❌ Indexing script missing"
fi

if [ -f "kilocode.yaml" ]; then
    echo "✅ Configuration file exists"
    COLLECTION=$(grep "collection_name:" kilocode.yaml | cut -d'"' -f2)
    echo "📋 Configured collection: ${COLLECTION:-kilocode_codebase}"
else
    echo "❌ Configuration file missing"
fi

# Check Python environment
echo ""
echo "=== PYTHON ENVIRONMENT ==="
if python3 -c "import qdrant_client, requests" 2>/dev/null; then
    echo "✅ Python dependencies available"
else
    echo "❌ Python dependencies missing"
    echo "   Run: pip3 install qdrant-client requests"
fi

echo ""
echo "=== STORAGE STATUS ==="
if [ -d "qdrant_storage" ]; then
    STORAGE_SIZE=$(du -sh qdrant_storage 2>/dev/null | cut -f1)
    echo "💾 Storage directory exists: $STORAGE_SIZE"
else
    echo "❌ Storage directory missing"
fi

echo ""
echo "=== RECOMMENDATIONS ==="
if ! curl -s http://localhost:6333/ > /dev/null 2>&1; then
    echo "🔧 Start Qdrant: docker run -d --name qdrant -p 6333:6333 -p 6334:6334 -v \$(pwd)/qdrant_storage:/qdrant/storage qdrant/qdrant"
fi

COLLECTION_EXISTS=$(curl -s http://localhost:6333/collections/kilocode_codebase 2>/dev/null | jq -r '.result // empty' 2>/dev/null || echo "")
if [ -z "$COLLECTION_EXISTS" ]; then
    echo "🔧 Run indexing: python3 4_Formula/check_and_index.py"
fi

echo ""
echo "📊 Inspection complete!"
```

## 📈 Performance Metrics

### Qdrant Performance

```bash
# Check memory usage
docker stats qdrant --no-stream

# Check disk I/O
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock dockerstats qdrant

# Get detailed metrics
curl -s http://localhost:6333/telemetry 2>/dev/null || echo "Telemetry not available"
```

### Indexing Performance

```bash
# Time the indexing process
time python3 4_Formula/check_and_index.py

# Check file processing rate
echo "Files processed per second: $(($(find . -type f -name "*.py" | wc -l) / $(time python3 4_Formula/check_and_index.py 2>&1 | grep "real" | cut -d'm' -f2 | cut -d's' -f1 | bc -l 2>/dev/null || echo "1")))"
```

## 🔄 Maintenance Operations

### Collection Management

```bash
# Recreate collection (WARNING: deletes all data)
curl -X DELETE http://localhost:6333/collections/kilocode_codebase

# Recreate with correct config
curl -X PUT http://localhost:6333/collections/kilocode_codebase \
  -H "Content-Type: application/json" \
  -d '{
    "vectors": {
      "size": 1536,
      "distance": "Cosine"
    }
  }'
```

### Data Backup

```bash
# Create snapshot
curl -X POST http://localhost:6333/collections/kilocode_codebase/snapshots

# List snapshots
curl -s http://localhost:6333/collections/kilocode_codebase/snapshots | jq '.result[]?.name'
```

### Cleanup

```bash
# Remove old snapshots
curl -X DELETE http://localhost:6333/collections/kilocode_codebase/snapshots/snapshot_name

# Optimize collection
curl -X POST http://localhost:6333/collections/kilocode_codebase/optimize
```

## 📋 Status Summary

Run this comprehensive check:

```bash
# Quick status
echo "Qdrant: $(curl -s http://localhost:6333/ > /dev/null && echo '✅ Running' || echo '❌ Down')"
echo "Collection: $(curl -s http://localhost:6333/collections/kilocode_codebase > /dev/null && echo '✅ Exists' || echo '❌ Missing')"
echo "Points: $(curl -s http://localhost:6333/collections/kilocode_codebase | jq '.result.points_count // 0')"
echo "Repo files: $(find . -type f \( -name "*.py" -o -name "*.js" -o -name "*.html" -o -name "*.md" \) | wc -l)"
```

This inspection provides complete visibility into both the Qdrant database state and repository indexing coverage.