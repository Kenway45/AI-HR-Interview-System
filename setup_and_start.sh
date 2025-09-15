#!/bin/bash

echo "🚀 AI HR Interview System - Complete Setup & Start"
echo "=================================================="
echo ""

# Check if we're in the right directory
if [[ ! -f "README.md" ]]; then
    echo "❌ Please run this script from the ai-hr-interview root directory"
    echo "   cd ~/Documents/ai-hr-interview"
    echo "   ./setup_and_start.sh"
    exit 1
fi

# Step 1: Install Docker if needed
echo "Step 1: Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    echo "🐳 Docker not found. Installing Docker..."
    ./infra/scripts/install_docker_mac.sh
    
    # Check if installation was successful
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker installation failed. Please install Docker manually:"
        echo "   https://docs.docker.com/desktop/install/mac-install/"
        exit 1
    fi
else
    echo "✅ Docker is installed: $(docker --version)"
    
    # Check if Docker is running
    if ! docker info &> /dev/null; then
        echo "⚠️  Docker is not running. Starting Docker Desktop..."
        open /Applications/Docker.app
        
        echo "⏳ Waiting for Docker to start..."
        for i in {1..30}; do
            if docker info &> /dev/null; then
                echo "✅ Docker is now running!"
                break
            fi
            echo -n "."
            sleep 2
        done
        
        if ! docker info &> /dev/null; then
            echo ""
            echo "❌ Docker failed to start. Please start Docker Desktop manually and try again."
            exit 1
        fi
    else
        echo "✅ Docker is running"
    fi
fi

# Step 2: Start the AI HR Interview System
echo ""
echo "Step 2: Starting AI HR Interview System..."
echo "========================================="

# Run the main startup script
./infra/scripts/start_system.sh

echo ""
echo "🎉 Setup complete!"
echo ""
echo "The AI HR Interview System should now be running at:"
echo "🌐 http://localhost:3000"
echo ""
echo "If you encounter any issues, check the logs with:"
echo "cd infra && docker-compose logs -f"
echo ""