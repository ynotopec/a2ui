#!/bin/bash

# A2UI Project - Quick Start Script
# This script helps you quickly start and test the A2UI streaming JSONL endpoint

set -e

echo "🚀 A2UI Project - Quick Start"
echo "=============================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first:"
    echo "   - On Ubuntu/Debian: sudo apt-get install docker.io docker-compose"
    echo "   - On macOS: brew install docker docker-compose"
    echo ""
    exit 1
fi

echo "✅ Docker is installed"
echo ""

# Check if vLLM is running
if curl -s http://localhost:8000/v1/models > /dev/null 2>&1; then
    echo "✅ vLLM service is already running on port 8000"
else
    echo "⚠️  vLLM service not running"
    echo ""
    echo "Starting vLLM and Agent services..."
    docker compose up -d vllm
    
    echo "Waiting for vLLM to start..."
    sleep 5
    
    echo "Starting agent service..."
    docker compose up -d agent
    
    echo "Waiting for agent to start..."
    sleep 3
fi

echo ""
echo "✅ Services are running"
echo ""

# Check if model directory exists
if [ ! -d "models/Qwen2.5-72B-Instruct" ]; then
    echo "⚠️  Model directory not found"
    echo ""
    echo "1. Download Qwen2.5-72B-Instruct from HuggingFace:"
    echo "   wget https://huggingface.co/Qwen/Qwen2.5-72B-Instruct/resolve/main/config.json -P models/Qwen2.5-72B-Instruct/"
    echo "   (Full model download is ~16GB - only needed if not using vLLM with cache)"
    echo ""
    echo "2. Or use HF cache: ./hf_cache"
fi

echo ""
echo "📊 Quick Tests"
echo "=============="
echo ""

# Test vLLM API
echo "1️⃣ Testing vLLM API..."
curl -s http://localhost:8000/v1/models | head -n 3
echo ""
echo ""

# Test agent endpoint
echo "2️⃣ Testing A2UI Agent..."
echo "Running: GET /a2ui?q=Hello&surface_id=test-surface"
curl -s -X GET "http://localhost:8080/a2ui?q=Hello&surface_id=test-surface" | head -n 20
echo "..."
echo ""

echo "📝 Testing JSONL streaming..."
echo "Running: curl -N 'http://localhost:8080/a2ui?q=Astuce+pour+gagner+en+productivité'"
echo ""
curl -N http://localhost:8080/a2ui?q=Astuce+pour+gagner+en+productivité
echo ""
echo ""
echo "✅ Tests completed!"
echo ""

# Show running services
echo "🔍 Running services:"
docker compose ps
echo ""

echo "📚 More information:"
echo "   - Quick Start: cat README.md"
echo "   - Architecture: cat docs/architecture.md"
echo "   - Use Cases: cat USE_CASE.md"
echo "   - Value: cat VALUE.md"
echo "   - Innovation Status: cat INNOVATION_STATUS.md"
echo ""

echo "🎮 Client testing:"
echo "   1. Open index.html in browser"
echo "   2. Or check client/public/index.html"
echo ""