#!/bin/bash

echo "Starting AI HR Interview System..."

# Check if docker and docker-compose are available
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed or not in PATH"
    echo "Please run: ./infra/scripts/install_docker_mac.sh"
    exit 1
fi

# Check Docker Compose (try both old and new syntax)
DOCKER_COMPOSE="docker-compose"
if ! command -v docker-compose &> /dev/null; then
    if docker compose version &> /dev/null 2>&1; then
        DOCKER_COMPOSE="docker compose"
        echo "Using new Docker Compose syntax: docker compose"
    else
        echo "Error: docker-compose is not installed or not in PATH"
        echo "Please run: ./infra/scripts/install_docker_mac.sh"
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

# Change to infra directory
cd "$(dirname "$0")/.."

echo "Building and starting all services..."

# First, download models and build whisper.cpp (one-time setup)
echo "Setting up models and whisper.cpp (this may take a while on first run)..."
$DOCKER_COMPOSE up model-downloader whisper-builder

# Start all services
echo "Starting main services..."
$DOCKER_COMPOSE up -d db minio judge0-db judge0-redis
sleep 10  # Wait for databases to be ready

$DOCKER_COMPOSE up -d judge0 textgen
sleep 15  # Wait for Judge0 and text-gen to be ready

$DOCKER_COMPOSE up -d whisper-server backend
sleep 5   # Wait for backend to be ready

$DOCKER_COMPOSE up -d frontend

echo ""
echo "✅ AI HR Interview System is starting up!"
echo ""
echo "Services will be available at:"
echo "  Frontend (React App):     http://localhost:3000"
echo "  Backend API:              http://localhost:8000"
echo "  API Documentation:        http://localhost:8000/docs"
echo "  MinIO Console:            http://localhost:9001 (admin/minioadmin)"
echo "  Text Generation WebUI:    http://localhost:5000"
echo "  Judge0 API:               http://localhost:2358"
echo "  Whisper Server:           http://localhost:8001"
echo ""
echo "⚠️  Initial startup may take several minutes as models are downloaded and services initialize."
echo ""
echo "To check service status:"
echo "  $DOCKER_COMPOSE ps"
echo ""
echo "To view logs:"
echo "  $DOCKER_COMPOSE logs -f [service_name]"
echo ""
echo "To stop all services:"
echo "  $DOCKER_COMPOSE down"
echo ""

# Wait a bit and check service health
echo "Checking service health in 30 seconds..."
sleep 30

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
check_service "Whisper Server" "http://localhost:8001/health"
check_service "Text Generation" "http://localhost:5000"
check_service "Judge0" "http://localhost:2358/system_info"
check_service "MinIO" "http://localhost:9000/minio/health/ready"

echo ""
echo "System startup complete! Visit http://localhost:3000 to begin."
echo ""