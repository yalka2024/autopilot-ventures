#!/bin/bash

# AutoPilot Ventures Platform - Deployment Script
# This script automates the deployment of the AutoPilot Ventures platform

set -e  # Exit on any error

echo "🚀 AutoPilot Ventures Platform - Deployment Script"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Check if Docker is installed
check_docker() {
    print_status "Checking Docker installation..."
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_success "Docker and Docker Compose are installed"
}

# Check if environment file exists
check_environment() {
    print_status "Checking environment configuration..."
    
    if [ ! -f ".env" ]; then
        print_warning "Environment file (.env) not found"
        if [ -f "env.template" ]; then
            print_status "Creating .env file from template..."
            cp env.template .env
            print_warning "Please edit .env file with your actual configuration values"
            print_warning "Then run this script again"
            exit 1
        else
            print_error "No environment template found. Please create .env file manually."
            exit 1
        fi
    fi
    
    print_success "Environment file found"
}

# Generate Fernet key if not exists
generate_fernet_key() {
    print_status "Checking Fernet key..."
    
    if ! grep -q "FERNET_KEY=" .env || grep -q "your_fernet_key_here" .env; then
        print_status "Generating new Fernet key..."
        python generate_fernet_key.py --save-env
        print_success "Fernet key generated and saved to .env"
    else
        print_success "Fernet key already configured"
    fi
}

# Run health check
run_health_check() {
    print_status "Running health check..."
    
    if python main.py --health-check; then
        print_success "Health check passed"
    else
        print_error "Health check failed. Please check your configuration."
        exit 1
    fi
}

# Build Docker images
build_images() {
    print_status "Building Docker images..."
    
    docker-compose build --no-cache
    print_success "Docker images built successfully"
}

# Start services
start_services() {
    print_status "Starting AutoPilot Ventures services..."
    
    docker-compose up -d
    
    print_success "Services started successfully"
    print_status "Waiting for services to be ready..."
    sleep 30
}

# Check service status
check_services() {
    print_status "Checking service status..."
    
    # Check if all containers are running
    if docker-compose ps | grep -q "Up"; then
        print_success "All services are running"
    else
        print_error "Some services failed to start"
        docker-compose logs
        exit 1
    fi
    
    # Check application health
    if curl -f http://localhost:8000/health &> /dev/null; then
        print_success "Application health check passed"
    else
        print_warning "Application health check failed (may still be starting up)"
    fi
}

# Display deployment information
display_info() {
    echo ""
    echo "🎉 AutoPilot Ventures Platform Deployment Complete!"
    echo "=================================================="
    echo ""
    echo "📊 Service URLs:"
    echo "   • Application: http://localhost:8000"
    echo "   • Prometheus:  http://localhost:9091"
    echo "   • Grafana:     http://localhost:3000 (admin/admin)"
    echo "   • MLflow:      http://localhost:5000"
    echo ""
    echo "🔧 Management Commands:"
    echo "   • View logs:     docker-compose logs -f"
    echo "   • Stop services: docker-compose down"
    echo "   • Restart:       docker-compose restart"
    echo "   • Health check:  python main.py --health-check"
    echo ""
    echo "📈 Monitoring:"
    echo "   • Open Grafana at http://localhost:3000"
    echo "   • Login with admin/admin"
    echo "   • Import the AutoPilot Ventures dashboard"
    echo ""
    echo "🚀 Next Steps:"
    echo "   1. Configure your API keys in the .env file"
    echo "   2. Set up your Stripe webhook for payments"
    echo "   3. Configure email/Slack alerts"
    echo "   4. Start autonomous operation: python main.py --start-autonomous"
    echo ""
}

# Main deployment process
main() {
    echo "Starting deployment process..."
    
    check_docker
    check_environment
    generate_fernet_key
    run_health_check
    build_images
    start_services
    check_services
    display_info
    
    print_success "Deployment completed successfully!"
}

# Run main function
main "$@" 