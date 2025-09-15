#!/bin/bash

# 🎤 CodeVox Production Setup
# Complete infrastructure with all AI services

set -e

echo "🏭 CodeVox Production Setup"
echo "=========================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔍 Checking requirements for production setup...${NC}"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is required for production setup${NC}"
    echo -e "${YELLOW}   Install from: https://docker.com/get-started${NC}"
    exit 1
fi

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is required${NC}"
    exit 1
fi

# Check available memory
MEMORY_GB=$(( $(sysctl hw.memsize | awk '{print $2}') / 1024 / 1024 / 1024 ))
if [ "$MEMORY_GB" -lt 8 ]; then
    echo -e "${YELLOW}⚠️  Warning: Recommended 8GB+ RAM for full AI models${NC}"
    echo -e "${YELLOW}   You have ${MEMORY_GB}GB. Consider using quick demo mode instead.${NC}"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 0
    fi
fi

echo -e "${GREEN}✅ Requirements met${NC}"
echo ""

echo -e "${BLUE}🏗️  Setting up CodeVox production environment...${NC}"

# Create necessary directories
mkdir -p data/models
mkdir -p data/uploads
mkdir -p data/sessions

echo -e "${YELLOW}📦 Pulling Docker images (this may take 10-15 minutes)...${NC}"
echo -e "${YELLOW}   • AI models will be downloaded (~3GB)${NC}"
echo -e "${YELLOW}   • Services will be configured${NC}"
echo ""

# Use the full docker-compose setup
cd infra

# Pull images first
docker-compose -f docker-compose.yml pull

echo -e "${GREEN}🚀 Starting CodeVox production services...${NC}"

# Start all services
docker-compose -f docker-compose.yml up -d

echo -e "${YELLOW}⏳ Waiting for services to initialize...${NC}"

# Wait for services to be healthy
timeout=300  # 5 minutes
counter=0

while [ $counter -lt $timeout ]; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend is ready${NC}"
        break
    fi
    
    echo -n "."
    sleep 2
    counter=$((counter + 2))
done

if [ $counter -ge $timeout ]; then
    echo -e "${RED}❌ Services failed to start within timeout${NC}"
    echo -e "${YELLOW}Check logs with: docker-compose logs${NC}"
    exit 1
fi

cd ..

echo ""
echo "🎉 CodeVox Production Environment is Ready!"
echo ""
echo -e "${GREEN}🌐 CodeVox Interface: http://localhost:3000${NC}"
echo -e "${BLUE}📚 API Documentation: http://localhost:8000/docs${NC}"
echo -e "${BLUE}🗄️  MinIO Console: http://localhost:9001 (minioadmin/minioadmin)${NC}"
echo -e "${BLUE}⚖️  Judge0 API: http://localhost:2358${NC}"
echo -e "${BLUE}🤖 AI Text Generation: http://localhost:5000${NC}"
echo ""
echo -e "${YELLOW}🏭 Production Features Enabled:${NC}"
echo "   ✅ Real AI models (Whisper, LLaMA)"
echo "   ✅ Secure code execution sandbox"
echo "   ✅ Scalable microservices architecture"
echo "   ✅ Persistent data storage"
echo "   ✅ Enterprise-grade monitoring"
echo ""
echo -e "${YELLOW}🛑 To stop all services:${NC}"
echo "   cd infra && docker-compose down"
echo ""
echo -e "${GREEN}Ready for serious interview practice! 🚀${NC}"