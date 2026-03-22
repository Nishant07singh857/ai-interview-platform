#!/bin/bash

# AI Interview Platform - Deployment Script
set -e

echo "🚀 Starting deployment of AI Interview Platform..."

# Configuration
ENVIRONMENT=${1:-production}
PROJECT_ROOT=$(pwd)
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
INFRA_DIR="$PROJECT_ROOT/infrastructure"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Helper functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is not installed"
        exit 1
    fi
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        log_error "Node.js is not installed"
        exit 1
    fi
    
    log_info "✓ All prerequisites satisfied"
}

setup_environment() {
    log_info "Setting up environment for $ENVIRONMENT..."
    
    # Copy appropriate environment file
    if [ "$ENVIRONMENT" = "production" ]; then
        cp "$BACKEND_DIR/.env.prod" "$BACKEND_DIR/.env" 2>/dev/null || log_warn "No .env.prod found"
        cp "$FRONTEND_DIR/.env.prod" "$FRONTEND_DIR/.env.local" 2>/dev/null || log_warn "No frontend .env.prod found"
    else
        cp "$BACKEND_DIR/.env.example" "$BACKEND_DIR/.env" 2>/dev/null || log_warn "No .env.example found"
        cp "$FRONTEND_DIR/.env.example" "$FRONTEND_DIR/.env.local" 2>/dev/null || log_warn "No frontend .env.example found"
    fi
    
    log_info "✓ Environment setup complete"
}

build_backend() {
    log_info "Building backend..."
    
    cd "$BACKEND_DIR"
    
    # Install Python dependencies
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements/prod.txt
    
    # Run tests
    log_info "Running backend tests..."
    pytest tests/ -v --cov=app --cov-report=xml
    
    # Build Docker image
    docker build -t ai-interview-backend:$ENVIRONMENT -f Dockerfile.prod .
    
    log_info "✓ Backend build complete"
}

build_frontend() {
    log_info "Building frontend..."
    
    cd "$FRONTEND_DIR"
    
    # Install dependencies
    npm ci
    
    # Run tests
    npm test
    
    # Build for production
    npm run build
    
    # Build Docker image
    docker build -t ai-interview-frontend:$ENVIRONMENT -f Dockerfile.prod .
    
    log_info "✓ Frontend build complete"
}

deploy_docker() {
    log_info "Deploying with Docker Compose..."
    
    cd "$PROJECT_ROOT"
    
    if [ "$ENVIRONMENT" = "production" ]; then
        docker-compose -f docker-compose.prod.yml down
        docker-compose -f docker-compose.prod.yml up -d --build
    else
        docker-compose down
        docker-compose up -d --build
    fi
    
    log_info "✓ Docker deployment complete"
}

setup_ssl() {
    if [ "$ENVIRONMENT" = "production" ]; then
        log_info "Setting up SSL certificates..."
        
        # Run certbot for SSL
        docker-compose -f docker-compose.prod.yml run --rm certbot certonly --webroot \
            --webroot-path=/var/www/certbot \
            --email admin@aiinterview.com \
            --agree-tos \
            --no-eff-email \
            -d aiinterview.com \
            -d www.aiinterview.com
        
        # Reload nginx to apply certificates
        docker-compose -f docker-compose.prod.yml exec nginx nginx -s reload
        
        log_info "✓ SSL setup complete"
    fi
}

run_database_migrations() {
    log_info "Running database migrations..."
    
    # Run Firebase indexes update
    firebase deploy --only firestore:indexes
    
    log_info "✓ Database migrations complete"
}

seed_database() {
    if [ "$ENVIRONMENT" != "production" ]; then
        log_info "Seeding database with test data..."
        
        cd "$BACKEND_DIR"
        source venv/bin/activate
        python -m scripts.seed_data
        
        log_info "✓ Database seeding complete"
    fi
}

setup_monitoring() {
    if [ "$ENVIRONMENT" = "production" ]; then
        log_info "Setting up monitoring..."
        
        # Deploy monitoring stack
        docker-compose -f docker-compose.monitoring.yml up -d
        
        log_info "✓ Monitoring setup complete"
    fi
}

run_health_checks() {
    log_info "Running health checks..."
    
    # Wait for services to start
    sleep 10
    
    # Check backend health
    if curl -f http://localhost:8000/health; then
        log_info "✓ Backend health check passed"
    else
        log_error "Backend health check failed"
        exit 1
    fi
    
    # Check frontend
    if curl -f http://localhost:3000; then
        log_info "✓ Frontend health check passed"
    else
        log_error "Frontend health check failed"
        exit 1
    fi
    
    log_info "✓ All health checks passed"
}

create_backup() {
    if [ "$ENVIRONMENT" = "production" ]; then
        log_info "Creating pre-deployment backup..."
        
        cd "$BACKEND_DIR"
        source venv/bin/activate
        python -m scripts.backup_db
        
        log_info "✓ Backup created"
    fi
}

notify_deployment() {
    if [ "$ENVIRONMENT" = "production" ]; then
        log_info "Sending deployment notification..."
        
        # Send to Slack webhook
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"🚀 AI Interview Platform deployed to production successfully!\"}" \
            "$SLACK_WEBHOOK_URL" 2>/dev/null || log_warn "Failed to send Slack notification"
        
        log_info "✓ Notification sent"
    fi
}

# Main deployment flow
main() {
    log_info "Starting deployment process for $ENVIRONMENT environment..."
    
    check_prerequisites
    create_backup
    setup_environment
    build_backend
    build_frontend
    deploy_docker
    setup_ssl
    run_database_migrations
    seed_database
    setup_monitoring
    run_health_checks
    notify_deployment
    
    log_info "✅ Deployment completed successfully!"
    log_info "🌐 Application is available at:"
    echo "   - Frontend: http://localhost:3000"
    echo "   - Backend API: http://localhost:8000"
    echo "   - API Docs: http://localhost:8000/api/docs"
}

# Run main function
main