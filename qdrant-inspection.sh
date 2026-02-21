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
    VERSION=$(curl -s http://localhost:6333/ | jq -r '.version // "unknown"' 2>/dev/null || echo "unknown")
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
    COLLECTION=$(grep "collection_name:" kilocode.yaml | cut -d'"' -f2 2>/dev/null || echo "kilocode_codebase")
    echo "📋 Configured collection: $COLLECTION"
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