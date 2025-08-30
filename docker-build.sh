#!/bin/bash

# Docker Build and Push Script for Watchtower V2
# Usage: ./docker-build.sh [registry] [tag] [push]
# ./docker-build.sh docker.io/zaidkaraymeh99 v1.0.1 push
set -e

# Configuration
IMAGE_NAME="watchtower"
DEFAULT_REGISTRY="docker.io/zaidkaraymeh99"
DEFAULT_TAG="latest"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Parse arguments
REGISTRY=${1:-$DEFAULT_REGISTRY}
TAG=${2:-$DEFAULT_TAG}
PUSH=${3:-false}

FULL_IMAGE_NAME="${REGISTRY}/${IMAGE_NAME}:${TAG}"

print_status "Building Docker image: ${FULL_IMAGE_NAME}"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Build the image
print_status "Building image..."
docker build -t "${FULL_IMAGE_NAME}" .

if [ $? -eq 0 ]; then
    print_success "Image built successfully!"
else
    print_error "Failed to build image"
    exit 1
fi

# Tag with latest if not already latest
if [ "$TAG" != "latest" ]; then
    print_status "Tagging as latest..."
    docker tag "${FULL_IMAGE_NAME}" "${REGISTRY}/${IMAGE_NAME}:latest"
fi

# Push to registry if requested
if [ "$PUSH" = "true" ] || [ "$PUSH" = "push" ]; then
    print_status "Pushing image to registry..."
    
    # Check if logged in to registry
    if ! docker info | grep -q "Username"; then
        print_warning "Not logged in to registry. Attempting to login..."
        docker login "${REGISTRY}"
    fi
    
    # Push the image
    docker push "${FULL_IMAGE_NAME}"
    
    if [ "$TAG" != "latest" ]; then
        docker push "${REGISTRY}/${IMAGE_NAME}:latest"
    fi
    
    print_success "Image pushed successfully!"
else
    print_status "Image built but not pushed. Use './docker-build.sh ${REGISTRY} ${TAG} push' to push."
fi

# Show image info
print_status "Image details:"
docker images | grep "${IMAGE_NAME}"

print_success "Build process completed!" 