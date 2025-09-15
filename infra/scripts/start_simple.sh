#!/bin/bash

echo "Starting AI HR Interview System (Simplified)"
echo "=========================================="

# Check if we're in the right directory
cd "$(dirname "$0")/.."

# Check Docker Compose (try both old and new syntax)
DOCKER_COMPOSE="docker-compose"
if ! command -v docker-compose &> /dev/null; then
    if docker compose version &> /dev/null 2>&1; then
        DOCKER_COMPOSE="docker compose"
        echo "Using new Docker Compose syntax: docker compose"
    else
        echo "Error: docker-compose is not installed or not in PATH"
        exit 1
    fi
else
    echo "Using Docker Compose: $(docker-compose --version)"
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "Error: Docker is installed but not running"
    echo "Please start Docker Desktop and try again"
    exit 1
fi

echo "Starting simplified services (Backend, Frontend, Database, Storage)..."

# Use the simplified docker-compose file
$DOCKER_COMPOSE -f docker-compose-simple.yml down
$DOCKER_COMPOSE -f docker-compose-simple.yml build
$DOCKER_COMPOSE -f docker-compose-simple.yml up -d

echo ""
echo "✅ AI HR Interview System (Demo Mode) is starting up!"
echo ""
echo "Services will be available at:"
echo "  🌐 Frontend (React App):     http://localhost:3000"
echo "  🔧 Backend API:              http://localhost:8000"
echo "  📖 API Documentation:        http://localhost:8000/docs"
echo "  💾 MinIO Console:            http://localhost:9001 (minioadmin/minioadmin)"
echo ""
echo "📝 Demo Mode Features:"
echo "  ✅ File upload and processing"
echo "  ✅ Mock interview questions"
echo "  ✅ Audio recording (mock transcription)"
echo "  ✅ Mock AI evaluation"
echo "  ✅ Proctoring simulation"
echo "  ✅ Report generation"
echo ""
echo "⚠️  Note: This is running in DEMO MODE with mock AI services."
echo "   Real STT and LLM services require additional setup."
echo ""

# Wait a bit and check service health
echo "Checking service health in 20 seconds..."
sleep 20

echo "Service Status:"
echo "==============="

# Check each service
check_service() {
    local service=$1
    local url=$2
    if curl -s "$url" > /dev/null 2>&1; then
        echo "✅ $service: Running"
    else
        echo "❌ $service: Not responding"
    fi
}

check_service "Frontend" "http://localhost:3000"
check_service "Backend API" "http://localhost:8000/health"
check_service "MinIO" "http://localhost:9000/minio/health/ready"

echo ""
echo "🎉 Demo system ready! Visit http://localhost:3000 to begin."
echo ""
echo "To stop all services:"
echo "  $DOCKER_COMPOSE -f docker-compose-simple.yml down"
echo ""