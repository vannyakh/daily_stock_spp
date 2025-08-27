#!/bin/bash

# Stock Data API Deployment Script (Supports V1 and V2)
# Usage: ./deploy.sh [staging|production|docker] [v1|v2]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Configuration
API_PORT=8000
DOCKER_IMAGE_V1="stock-data-api-v1"
DOCKER_IMAGE_V2="stock-data-api-v2"
DOCKER_TAG="latest"

# Default values
DEPLOY_ENV="staging"
API_VERSION="v2"

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

log_version() {
    echo -e "${PURPLE}🔀 $1${NC}"
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

test_v1_api() {
    log_info "Testing V1 API functionality..."
    
    # Test if the V1 API can be imported
    python3 -c "
import sys
sys.path.append('v1')
from stock_api import app
print('✅ V1 API app imported successfully')
print(f'✅ App title: {app.title}')
print(f'✅ App version: {app.version}')
print('✅ V1 API test completed')
"
    
    log_success "V1 API test passed"
}

test_v2_api() {
    log_info "Testing V2 API functionality..."
    
    # Test if the V2 API can be imported
    python3 -c "
import sys
sys.path.append('v2')
from stock_api_server import app
print('✅ V2 API app imported successfully')
print(f'✅ App title: {app.title}')
print(f'✅ App version: {app.version}')
print('✅ V2 API test completed')
"
    
    log_success "V2 API test passed"
}

test_api() {
    if [[ "$API_VERSION" == "v1" ]]; then
        test_v1_api
    else
        test_v2_api
    fi
}

deploy_staging() {
    log_info "Deploying $API_VERSION API to staging environment..."
    
    # Create staging directory
    mkdir -p staging/$API_VERSION
    cd staging/$API_VERSION
    
    if [[ "$API_VERSION" == "v1" ]]; then
        # V1 deployment
        cp ../../v1/stock_api.py .
        cp ../../requirements.txt .
        cp -r ../../stock_data . 2>/dev/null || log_warning "No stock_data folder found"
        log_info "V1 Basic API deployed with intraday data support"
    else
        # V2 deployment
        cp ../../v2/stock_api_server.py .
        cp ../../requirements.txt .
        cp -r ../../json_stock_data . 2>/dev/null || log_warning "No json_stock_data folder found"
        cp -r ../../stock_data . 2>/dev/null || log_warning "No stock_data folder found"
        log_info "V2 Enhanced API deployed with comprehensive data support"
    fi
    
    # Install dependencies in staging
    pip3 install -r requirements.txt
    
    log_success "Staging deployment completed for $API_VERSION"
    log_info "To start staging API: cd staging/$API_VERSION && python3 $(if [[ "$API_VERSION" == "v1" ]]; then echo "stock_api.py"; else echo "stock_api_server.py"; fi)"
    
    cd ../..
}

deploy_production() {
    log_info "Deploying $API_VERSION API to production environment..."
    
    # Create production directory
    mkdir -p production/$API_VERSION
    cd production/$API_VERSION
    
    if [[ "$API_VERSION" == "v1" ]]; then
        # V1 deployment
        cp ../../v1/stock_api.py .
        cp ../../requirements.txt .
        cp -r ../../stock_data . 2>/dev/null || log_warning "No stock_data folder found"
        log_info "V1 Basic API deployed to production"
    else
        # V2 deployment
        cp ../../v2/stock_api_server.py .
        cp ../../requirements.txt .
        cp -r ../../json_stock_data . 2>/dev/null || log_warning "No json_stock_data folder found"
        cp -r ../../stock_data . 2>/dev/null || log_warning "No stock_data folder found"
        log_info "V2 Enhanced API deployed to production"
    fi
    
    # Install dependencies in production
    pip3 install -r requirements.txt
    
    log_success "Production deployment completed for $API_VERSION"
    log_info "To start production API: cd production/$API_VERSION && python3 $(if [[ "$API_VERSION" == "v1" ]]; then echo "stock_api.py"; else echo "stock_api_server.py"; fi)"
    
    cd ../..
}

deploy_docker() {
    log_info "Deploying $API_VERSION API with Docker..."
    
    # Build Docker image for the selected version
    if [[ "$API_VERSION" == "v1" ]]; then
        log_info "Building V1 Docker image..."
        docker build -t $DOCKER_IMAGE_V1:$DOCKER_TAG -f Dockerfile.v1 .
        
        # Test Docker image
        log_info "Testing V1 Docker image..."
        docker run --rm -d --name test-api-v1 -p $API_PORT:$API_PORT $DOCKER_IMAGE_V1:$DOCKER_TAG
        
        # Wait for API to start
        sleep 10
        
        # Test API health
        if curl -f http://localhost:$API_PORT/api/health > /dev/null 2>&1; then
            log_success "V1 Docker API test passed"
        else
            log_error "V1 Docker API test failed"
            docker stop test-api-v1
            exit 1
        fi
        
        # Stop test container
        docker stop test-api-v1
        
        log_success "V1 Docker deployment completed"
        log_info "To run V1 API with Docker: docker run -p $API_PORT:$API_PORT $DOCKER_IMAGE_V1:$DOCKER_TAG"
    else
        log_info "Building V2 Docker image..."
        docker build -t $DOCKER_IMAGE_V2:$DOCKER_TAG -f Dockerfile.v2 .
        
        # Test Docker image
        log_info "Testing V2 Docker image..."
        docker run --rm -d --name test-api-v2 -p $API_PORT:$API_PORT $DOCKER_IMAGE_V2:$DOCKER_TAG
        
        # Wait for API to start
        sleep 10
        
        # Test API health
        if curl -f http://localhost:$API_PORT/ > /dev/null 2>&1; then
            log_success "V2 Docker API test passed"
        else
            log_error "V2 Docker API test failed"
            docker stop test-api-v2
            exit 1
        fi
        
        # Stop test container
        docker stop test-api-v2
        
        log_success "V2 Docker deployment completed"
        log_info "To run V2 API with Docker: docker run -p $API_PORT:$API_PORT $DOCKER_IMAGE_V2:$DOCKER_TAG"
    fi
}

deploy_compose() {
    log_info "Deploying $API_VERSION API with Docker Compose..."
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "docker-compose is not installed"
        exit 1
    fi
    
    # Set environment variable for the selected version
    export API_VERSION=$API_VERSION
    
    # Start services
    docker-compose up -d
    
    log_success "Docker Compose deployment completed for $API_VERSION"
    log_info "Services available at:"
    log_info "  - API: http://localhost:8000"
    log_info "  - Nginx: http://localhost:80"
    log_info "  - Prometheus: http://localhost:9090"
    log_info "  - Grafana: http://localhost:3000 (admin/admin)"
}

show_status() {
    log_info "Deployment Status for $API_VERSION:"
    
    # Check if API is running
    if curl -f http://localhost:$API_PORT/$(if [[ "$API_VERSION" == "v1" ]]; then echo "api/health"; else echo ""; fi) > /dev/null 2>&1; then
        log_success "$API_VERSION API is running on port $API_PORT"
    else
        log_warning "$API_VERSION API is not running on port $API_PORT"
    fi
    
    # Check Docker containers
    if command -v docker &> /dev/null; then
        log_info "Docker containers:"
        if [[ "$API_VERSION" == "v1" ]]; then
            docker ps --filter "name=stock-data-api-v1" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        else
            docker ps --filter "name=stock-data-api-v2" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        fi
    fi
    
    # Show data status
    log_info "Data Status:"
    if [[ "$API_VERSION" == "v1" ]]; then
        if [ -d "stock_data" ]; then
            v1_count=$(find stock_data -name "*_intraday.csv" | wc -l)
            log_success "V1 Basic data: $v1_count stocks available"
        else
            log_warning "V1 Basic data: No data found"
        fi
    else
        if [ -d "json_stock_data" ]; then
            v2_count=$(find json_stock_data -name "*_comprehensive.json" | wc -l)
            market_count=$(find json_stock_data -name "market_overview.json" | wc -l)
            log_success "V2 Enhanced data: $v2_count stocks available"
            log_success "V2 Market data: $market_count files available"
        else
            log_warning "V2 Enhanced data: No data found"
        fi
    fi
}

show_help() {
    echo "Stock Data API Deployment Script (Supports V1 and V2)"
    echo ""
    echo "Usage: $0 [ENVIRONMENT] [VERSION]"
    echo ""
    echo "Environments:"
    echo "  staging     Deploy to staging environment"
    echo "  production  Deploy to production environment"
    echo "  docker      Deploy using Docker"
    echo "  compose     Deploy using Docker Compose (full stack)"
    echo "  status      Show deployment status"
    echo "  help        Show this help message"
    echo ""
    echo "Versions:"
    echo "  v1          Basic Stock Data API (intraday data)"
    echo "  v2          Enhanced Stock Data API (comprehensive data)"
    echo ""
    echo "Examples:"
    echo "  $0 staging v1     # Deploy V1 API to staging"
    echo "  $0 production v2  # Deploy V2 API to production"
    echo "  $0 docker v1      # Deploy V1 API with Docker"
    echo "  $0 status v2      # Check V2 API deployment status"
    echo ""
    echo "Default: staging v2 (if no arguments provided)"
}

# Parse command line arguments
parse_args() {
    if [[ $# -ge 1 ]]; then
        DEPLOY_ENV="$1"
    fi
    
    if [[ $# -ge 2 ]]; then
        API_VERSION="$2"
    fi
    
    # Validate API version
    if [[ "$API_VERSION" != "v1" && "$API_VERSION" != "v2" ]]; then
        log_error "Invalid API version: $API_VERSION. Use 'v1' or 'v2'"
        exit 1
    fi
    
    # Validate deployment environment
    case "$DEPLOY_ENV" in
        "staging"|"production"|"docker"|"compose"|"status"|"help")
            ;;
        *)
            log_error "Invalid deployment environment: $DEPLOY_ENV"
            show_help
            exit 1
            ;;
    esac
}

# Main script
main() {
    parse_args "$@"
    
    log_version "Deploying $API_VERSION API to $DEPLOY_ENV environment"
    
    case "$DEPLOY_ENV" in
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
        "help")
            show_help
            ;;
    esac
    
    log_success "Deployment completed successfully for $API_VERSION!"
}

# Run main function
main "$@"
