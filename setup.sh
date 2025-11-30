#!/bin/bash

# Clinical Trials Blockchain Platform Setup Script

set -e

echo "=========================================="
echo "Clinical Trials Blockchain Platform Setup"
echo "=========================================="
echo ""

# Check prerequisites
echo "Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Prerequisites check passed"
echo ""

# Create .env files if they don't exist
echo "Setting up environment files..."

if [ ! -f backend/.env ]; then
    echo "Creating backend/.env from .env.example..."
    cp backend/.env.example backend/.env
    echo "⚠️  Please update backend/.env with your configuration"
fi

if [ ! -f frontend/.env.local ]; then
    echo "Creating frontend/.env.local from .env.example..."
    cp frontend/.env.example frontend/.env.local
fi

echo "✅ Environment files created"
echo ""

# Build and start services
echo "Building Docker images..."
docker-compose build

echo ""
echo "Starting services..."
docker-compose up -d

echo ""
echo "Waiting for services to be ready..."
sleep 10

# Initialize database
echo "Initializing database..."
docker-compose exec -T backend python -c "from database import init_db; init_db()" || echo "Database initialization may have failed - check logs"

echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "Services are running:"
echo "  - Frontend: http://localhost:3000"
echo "  - Backend API: http://localhost:8000"
echo "  - API Docs: http://localhost:8000/docs"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f"
echo ""
echo "To stop services:"
echo "  docker-compose down"
echo ""

