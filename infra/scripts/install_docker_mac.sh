#!/bin/bash

echo "🐳 Installing Docker on macOS"
echo "=============================="

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "📦 Installing Homebrew first..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # Add Homebrew to PATH for this session
    if [[ -f "/opt/homebrew/bin/brew" ]]; then
        # Apple Silicon Mac
        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
        eval "$(/opt/homebrew/bin/brew shellenv)"
    else
        # Intel Mac
        echo 'eval "$(/usr/local/bin/brew shellenv)"' >> ~/.zprofile
        eval "$(/usr/local/bin/brew shellenv)"
    fi
    
    echo "✅ Homebrew installed successfully"
else
    echo "✅ Homebrew is already installed"
fi

# Update Homebrew
echo "🔄 Updating Homebrew..."
brew update

# Check if Docker is already installed
if command -v docker &> /dev/null; then
    echo "✅ Docker is already installed: $(docker --version)"
    
    # Check if Docker is running
    if docker info &> /dev/null; then
        echo "✅ Docker is running"
    else
        echo "⚠️  Docker is installed but not running"
        echo "Starting Docker Desktop..."
        open /Applications/Docker.app
        echo "Please wait for Docker Desktop to start (look for the whale icon in your menu bar)"
        echo "Then re-run this script to continue"
        exit 1
    fi
else
    echo "📦 Installing Docker Desktop..."
    brew install --cask docker
    
    echo "🚀 Starting Docker Desktop..."
    open /Applications/Docker.app
    
    echo ""
    echo "⏳ Waiting for Docker Desktop to start..."
    echo "   This may take a few minutes on first launch."
    echo "   Look for the Docker whale icon in your menu bar."
    echo ""
    
    # Wait for Docker to start
    for i in {1..60}; do
        if docker info &> /dev/null; then
            echo "✅ Docker is now running!"
            break
        fi
        echo -n "."
        sleep 5
    done
    
    if ! docker info &> /dev/null; then
        echo ""
        echo "❌ Docker failed to start automatically"
        echo "Please:"
        echo "1. Open Docker Desktop manually from Applications"
        echo "2. Wait for it to start completely"
        echo "3. Re-run this script"
        exit 1
    fi
fi

# Verify Docker Compose
if command -v docker-compose &> /dev/null; then
    echo "✅ Docker Compose is available: $(docker-compose --version)"
else
    # Try docker compose (newer syntax)
    if docker compose version &> /dev/null; then
        echo "✅ Docker Compose is available: $(docker compose version)"
        # Create an alias for older syntax
        echo 'alias docker-compose="docker compose"' >> ~/.zshrc
    else
        echo "❌ Docker Compose not found"
        exit 1
    fi
fi

echo ""
echo "🎉 Docker installation completed successfully!"
echo ""
echo "Docker version: $(docker --version)"
echo "Docker Compose: $(docker-compose --version 2>/dev/null || docker compose version)"
echo ""
echo "You can now run the AI HR Interview System:"
echo "cd ~/Documents/ai-hr-interview"
echo "./infra/scripts/start_system.sh"
echo ""