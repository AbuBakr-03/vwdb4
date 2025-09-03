#!/bin/bash

# Deployment Script for Watchtower V2
# Usage: ./deploy.sh [environment] [action]


set -e

# Configuration
ENVIRONMENT=${1:-staging}
ACTION=${2:-deploy}
IMAGE_NAME="watchtower"
REGISTRY="zaidkaraymeh"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(staging|production)$ ]]; then
    print_error "Invalid environment. Use 'staging' or 'production'"
    exit 1
fi

# Validate action
if [[ ! "$ACTION" =~ ^(deploy|rollback|status|logs)$ ]]; then
    print_error "Invalid action. Use 'deploy', 'rollback', 'status', or 'logs'"
    exit 1
fi

print_status "Deploying to ${ENVIRONMENT} environment..."

case $ACTION in
    "deploy")
        deploy_environment
        ;;
    "rollback")
        rollback_environment
        ;;
    "status")
        check_status
        ;;
    "logs")
        show_logs
        ;;
esac

deploy_environment() {
    print_status "Starting deployment to ${ENVIRONMENT}..."
    
    # Pull latest image
    print_status "Pulling latest image..."
    docker pull ${REGISTRY}/${IMAGE_NAME}:latest
    
    # Tag with environment
    docker tag ${REGISTRY}/${IMAGE_NAME}:latest ${REGISTRY}/${IMAGE_NAME}:${ENVIRONMENT}
    
    # Stop current services
    print_status "Stopping current services..."
    docker-compose -f docker-compose.${ENVIRONMENT}.yml down
    
    # Start new services
    print_status "Starting new services..."
    docker-compose -f docker-compose.${ENVIRONMENT}.yml up -d
    
    # Wait for health check
    print_status "Waiting for health check..."
    sleep 30
    
    # Check health
    if curl -f http://localhost:8000/health/ > /dev/null 2>&1; then
        print_success "Deployment successful! Health check passed."
    else
        print_error "Deployment failed! Health check failed."
        exit 1
    fi
}

rollback_environment() {
    print_status "Rolling back ${ENVIRONMENT} environment..."
    
    # Stop current services
    docker-compose -f docker-compose.${ENVIRONMENT}.yml down
    
    # Start previous version (you might want to implement version tracking)
    docker-compose -f docker-compose.${ENVIRONMENT}.yml up -d
    
    print_success "Rollback completed!"
}

check_status() {
    print_status "Checking ${ENVIRONMENT} environment status..."
    docker-compose -f docker-compose.${ENVIRONMENT}.yml ps
}

show_logs() {
    print_status "Showing ${ENVIRONMENT} environment logs..."
    docker-compose -f docker-compose.${ENVIRONMENT}.yml logs -f
}

print_success "Deployment script completed!" 