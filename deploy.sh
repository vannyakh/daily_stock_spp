#!/bin/bash

# Stock Data API Deployment Script
# Usage: ./deploy.sh [staging|production|docker]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
API_PORT=8000
DOCKER_IMAGE="stock-data-api"
DOCKER_TAG="latest"

# Functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

check_dependencies() {
    log_info "Checking dependencies..."
    
    # Check if Python is installed
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 is not installed"
        exit 1
    fi
    
    # Check if pip is installed
    if ! command -v pip3 &> /dev/null; then
        log_error "pip3 is not installed"
        exit 1
    fi
    
    # Check if Docker is installed (for Docker deployment)
    if [[ "$1" == "docker" ]] && ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    log_success "All dependencies are available"
}

install_dependencies() {
    log_info "Installing Python dependencies..."
    pip3 install -r requirements.txt
    log_success "Dependencies installed successfully"
}

test_api() {
    log_info "Testing API functionality..."
    
    # Test if the API can be imported
    python3 -c "
import sys
sys.path.append('.')
from stock_api import app
print('✅ API app imported successfully')
print(f'✅ App title: {app.title}')
print(f'✅ App version: {app.version}')
"
    
    log_success "API test passed"
}

deploy_staging() {
    log_info "Deploying to staging environment..."
    
    # Create staging directory
    mkdir -p staging
    cp stock_api.py staging/
    cp requirements.txt staging/
    cp -r stock_data staging/ 2>/dev/null || log_warning "No stock_data folder found"
    
    # Install dependencies in staging
    cd staging
    pip3 install -r requirements.txt
    
    log_success "Staging deployment completed"
    log_info "To start staging API: cd staging && python3 stock_api.py"
    
    cd ..
}

deploy_production() {
    log_info "Deploying to production environment..."
    
    # Create production directory
    mkdir -p production
    cp stock_api.py production/
    cp requirements.txt production/
    cp -r stock_data production/ 2>/dev/null || log_warning "No stock_data folder found"
    
    # Install dependencies in production
    cd production
    pip3 install -r requirements.txt
    
    log_success "Production deployment completed"
    log_info "To start production API: cd production && python3 stock_api.py"
    
    cd ..
}

deploy_docker() {
    log_info "Deploying with Docker..."
    
    # Build Docker image
    log_info "Building Docker image..."
    docker build -t $DOCKER_IMAGE:$DOCKER_TAG .
    
    # Test Docker image
    log_info "Testing Docker image..."
    docker run --rm -d --name test-api -p $API_PORT:$API_PORT $DOCKER_IMAGE:$DOCKER_TAG
    
    # Wait for API to start
    sleep 10
    
    # Test API health
    if curl -f http://localhost:$API_PORT/api/health > /dev/null 2>&1; then
        log_success "Docker API test passed"
    else
        log_error "Docker API test failed"
        docker stop test-api
        exit 1
    fi
    
    # Stop test container
    docker stop test-api
    
    log_success "Docker deployment completed"
    log_info "To run with Docker: docker run -p $API_PORT:$API_PORT $DOCKER_IMAGE:$DOCKER_TAG"
}

deploy_compose() {
    log_info "Deploying with Docker Compose..."
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "docker-compose is not installed"
        exit 1
    fi
    
    # Start services
    docker-compose up -d
    
    log_success "Docker Compose deployment completed"
    log_info "Services available at:"
    log_info "  - API: http://localhost:8000"
    log_info "  - Nginx: http://localhost:80"
    log_info "  - Prometheus: http://localhost:9090"
    log_info "  - Grafana: http://localhost:3000 (admin/admin)"
}

show_status() {
    log_info "Deployment Status:"
    
    # Check if API is running
    if curl -f http://localhost:$API_PORT/api/health > /dev/null 2>&1; then
        log_success "API is running on port $API_PORT"
    else
        log_warning "API is not running on port $API_PORT"
    fi
    
    # Check Docker containers
    if command -v docker &> /dev/null; then
        log_info "Docker containers:"
        docker ps --filter "name=stock" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    fi
}

show_help() {
    echo "Stock Data API Deployment Script"
    echo ""
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  staging     Deploy to staging environment"
    echo "  production  Deploy to production environment"
    echo "  docker      Deploy using Docker"
    echo "  compose     Deploy using Docker Compose (full stack)"
    echo "  status      Show deployment status"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 staging     # Deploy to staging"
    echo "  $0 docker      # Deploy with Docker"
    echo "  $0 status      # Check deployment status"
}

# Main script
main() {
    case "${1:-help}" in
        "staging")
            check_dependencies
            install_dependencies
            test_api
            deploy_staging
            ;;
        "production")
            check_dependencies
            install_dependencies
            test_api
            deploy_production
            ;;
        "docker")
            check_dependencies docker
            install_dependencies
            test_api
            deploy_docker
            ;;
        "compose")
            check_dependencies docker
            deploy_compose
            ;;
        "status")
            show_status
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# Run main function
main "$@"
