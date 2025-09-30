#!/bin/bash

# Crane Intelligence Platform - Production Deployment Script
# This script deploys the platform to production

set -e

echo "🚀 Starting Crane Intelligence Platform Deployment..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p logs
mkdir -p data
mkdir -p backups
mkdir -p ssl

# Set proper permissions
echo "🔐 Setting permissions..."
chmod 755 logs
chmod 755 data
chmod 755 backups
chmod 700 ssl

# Copy environment file
if [ ! -f .env ]; then
    echo "📋 Creating environment file..."
    cp env.production .env
    echo "⚠️  Please update .env file with your production values"
fi

# Build and start services
echo "🔨 Building and starting services..."
docker-compose down --remove-orphans
docker-compose build --no-cache
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check service health
echo "🏥 Checking service health..."
if curl -f http://localhost:8003/health > /dev/null 2>&1; then
    echo "✅ Backend service is healthy"
else
    echo "❌ Backend service is not responding"
    exit 1
fi

if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend service is healthy"
else
    echo "❌ Frontend service is not responding"
    exit 1
fi

# Initialize database
echo "🗄️ Initializing database..."
docker-compose exec backend python init_equipment_db.py

echo "🎉 Deployment completed successfully!"
echo ""
echo "🌐 Access Points:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8003"
echo "   API Docs: http://localhost:8003/docs"
echo ""
echo "📊 Service Status:"
docker-compose ps

