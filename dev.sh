#!/bin/bash

# Development startup script with hot reload
echo "🚀 Starting Watchtower V2 Development Environment..."

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose down

# Build and start with development settings
echo "🔨 Building and starting development environment..."
docker-compose up --build

echo "✅ Development environment started!"
echo "🌐 Your app should be available at: http://localhost:8000"
echo "📝 Make changes to your code and they will automatically reload!"
echo "🛑 Press Ctrl+C to stop the development server" 