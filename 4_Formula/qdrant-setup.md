# Qdrant Setup and Operation Guide

This document provides comprehensive instructions for setting up and running Qdrant vector database for the Stream Deck project.

## 📋 Prerequisites

- Docker installed and running
- At least 2GB free RAM
- 5GB free disk space for data storage

## 🚀 Quick Start

### One-Line Command
```bash
docker run -d --name qdrant \
  -p 6333:6333 -p 6334:6334 \
  -v $(pwd)/qdrant_storage:/qdrant/storage \
  qdrant/qdrant
```

### Verify Installation
```bash
# Check if container is running
docker ps | grep qdrant

# Check health endpoint
curl -s http://localhost:6333/health

# Check dashboard (if available)
curl -s http://localhost:6333/dashboard
```

## 📊 Detailed Setup

### 1. Create Storage Directory
```bash
# Create persistent storage directory
mkdir -p qdrant_storage

# Set proper permissions
chmod 755 qdrant_storage
```

### 2. Run Qdrant Container
```bash
# Basic run command
docker run -d \
  --name qdrant \
  -p 6333:6333 \
  -p 6334:6334 \
  -v $(pwd)/qdrant_storage:/qdrant/storage \
  qdrant/qdrant
```

### 3. Environment Variables (Optional)
```bash
# With custom configuration
docker run -d \
  --name qdrant \
  -p 6333:6333 \
  -p 6334:6334 \
  -e QDRANT__SERVICE__HTTP_PORT=6333 \
  -e QDRANT__SERVICE__GRPC_PORT=6334 \
  -v $(pwd)/qdrant_storage:/qdrant/storage \
  qdrant/qdrant
```

## 🔍 Health Checks

### Basic Health Check
```bash
# HTTP health check
curl -X GET http://localhost:6333/health

# Expected response:
# {"status":"ok","version":"1.7.4"}
```

### Detailed Status
```bash
# Get server info
curl -X GET http://localhost:6333/

# Check telemetry (if enabled)
curl -X GET http://localhost:6333/telemetry
```

## 📈 Collection Management

### Create Collection for Kilo Code
```bash
# Create collection with cosine similarity
curl -X PUT http://localhost:6333/collections/kilocode_codebase \
  -H "Content-Type: application/json" \
  -d '{
    "vectors": {
      "size": 1536,
      "distance": "Cosine"
    }
  }'
```

### Check Collection Status
```bash
# Get collection info
curl -X GET http://localhost:6333/collections/kilocode_codebase

# Get collection points count
curl -X GET http://localhost:6333/collections/kilocode_codebase | jq '.result.points_count'
```

### List All Collections
```bash
curl -X GET http://localhost:6333/collections
```

## 🔧 Management Commands

### Stop Qdrant
```bash
# Stop container
docker stop qdrant

# Remove container (keeps data)
docker rm qdrant
```

### Restart Qdrant
```bash
# Start existing container
docker start qdrant

# Or recreate
docker run -d --name qdrant \
  -p 6333:6333 -p 6334:6334 \
  -v $(pwd)/qdrant_storage:/qdrant/storage \
  qdrant/qdrant
```

### View Logs
```bash
# View recent logs
docker logs qdrant

# Follow logs
docker logs -f qdrant
```

### Backup Data
```bash
# Create backup
docker run --rm \
  -v $(pwd)/qdrant_storage:/qdrant/storage \
  -v $(pwd)/qdrant_backup:/backup \
  qdrant/qdrant \
  qdrant-backup --uri http://host.docker.internal:6333 create --collection kilocode_codebase --backup-dir /backup
```

## 📊 Monitoring

### Real-time Monitoring
```bash
# Watch health status
watch -n 5 'curl -s http://localhost:6333/health | jq ".status"'

# Monitor collection size
watch -n 10 'curl -s http://localhost:6333/collections/kilocode_codebase | jq ".result.points_count // 0"'
```

### Performance Metrics
```bash
# Get cluster info
curl -X GET http://localhost:6333/cluster

# Check disk usage
du -sh qdrant_storage/

# Check memory usage
docker stats qdrant
```

## 🐛 Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Find what's using the port
lsof -i :6333

# Kill process using port
kill -9 <PID>

# Or use different ports
docker run -d --name qdrant \
  -p 6334:6333 -p 6335:6334 \
  qdrant/qdrant
```

#### Permission Issues
```bash
# Fix storage permissions
sudo chown -R $USER:$USER qdrant_storage

# Or run container as current user
docker run -d --user $(id -u):$(id -g) \
  --name qdrant \
  -p 6333:6333 \
  -v $(pwd)/qdrant_storage:/qdrant/storage \
  qdrant/qdrant
```

#### Out of Memory
```bash
# Limit memory usage
docker run -d --name qdrant \
  --memory=2g \
  --memory-swap=4g \
  -p 6333:6333 \
  -v $(pwd)/qdrant_storage:/qdrant/storage \
  qdrant/qdrant
```

#### Data Corruption
```bash
# Clear storage and restart
docker stop qdrant
docker rm qdrant
rm -rf qdrant_storage/*
docker run -d --name qdrant \
  -p 6333:6333 \
  -v $(pwd)/qdrant_storage:/qdrant/storage \
  qdrant/qdrant
```

## ⚙️ Advanced Configuration

### Custom Configuration File
```bash
# Create config file
cat > qdrant_config.yaml << EOF
service:
  http_port: 6333
  grpc_port: 6334
storage:
  storage_path: /qdrant/storage
  snapshots_path: /qdrant/snapshots
  temp_path: /tmp
  wal_path: /qdrant/wal
  performance:
    max_search_threads: 4
  optimizers:
    deleted_threshold: 0.2
    vacuum_min_vector_number: 1000
    default_segment_number: 2
    memmap_threshold: 100000
EOF

# Run with config
docker run -d --name qdrant \
  -p 6333:6333 \
  -v $(pwd)/qdrant_config.yaml:/qdrant/config/production.yaml \
  -v $(pwd)/qdrant_storage:/qdrant/storage \
  qdrant/qdrant \
  --config-path /qdrant/config/production.yaml
```

### Docker Compose Setup
```yaml
# docker-compose.yml
version: '3.8'
services:
  qdrant:
    image: qdrant/qdrant
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - ./qdrant_storage:/qdrant/storage
    environment:
      - QDRANT__SERVICE__HTTP_PORT=6333
      - QDRANT__SERVICE__GRPC_PORT=6334
    restart: unless-stopped
```

## 🔗 Integration with Kilo Code

### Required Settings
- **Host**: `http://localhost:6333`
- **Collection**: `kilocode_codebase`
- **Vector Size**: `1536`
- **Distance**: `Cosine`

### Testing Connection
```bash
# Test basic connectivity
curl -X GET http://localhost:6333/health

# Test collection access
curl -X GET http://localhost:6333/collections/kilocode_codebase

# Test search (example)
curl -X POST http://localhost:6333/collections/kilocode_codebase/points/search \
  -H "Content-Type: application/json" \
  -d '{
    "vector": [0.1, 0.2, 0.3],
    "limit": 10
  }'
```

## 📚 API Reference

### REST API Endpoints
- `GET /health` - Health check
- `GET /` - Server info
- `GET /collections` - List collections
- `PUT /collections/{name}` - Create collection
- `GET /collections/{name}` - Get collection info
- `POST /collections/{name}/points/search` - Search vectors

### Useful Commands
```bash
# Get API documentation
curl -s http://localhost:6333/ | jq '.openapi'

# Check version
curl -s http://localhost:6333/ | jq '.version'
```

## 🎯 Quick Reference

### Start: `docker run -d --name qdrant -p 6333:6333 -p 6334:6334 -v $(pwd)/qdrant_storage:/qdrant/storage qdrant/qdrant`
### Stop: `docker stop qdrant && docker rm qdrant`
### Health: `curl -s http://localhost:6333/health`
### Status: `docker ps | grep qdrant`
### Logs: `docker logs qdrant`

Qdrant is now ready for vector storage and semantic search operations!