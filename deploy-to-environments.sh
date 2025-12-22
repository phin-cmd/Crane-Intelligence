#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================="
echo "Crane Intelligence - Environment Deployment"
echo "========================================="
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if docker compose is available
if command -v docker compose &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
elif command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
else
    print_error "Neither 'docker compose' nor 'docker-compose' is available. Please install Docker Compose."
    exit 1
fi

print_status "Using: $DOCKER_COMPOSE"
echo ""

# Function to deploy to an environment
deploy_environment() {
    local ENV_NAME=$1
    local COMPOSE_FILE=$2
    local PROJECT_NAME=$3
    local ENV_FILE=$4
    
    print_step "Deploying to $ENV_NAME environment..."
    echo ""
    
    # Check if env file exists
    if [ ! -f "$ENV_FILE" ]; then
        print_warning "Environment file $ENV_FILE not found. Creating from template if available..."
        if [ -f "${ENV_FILE}.template" ]; then
            cp "${ENV_FILE}.template" "$ENV_FILE"
            chmod 600 "$ENV_FILE"
            print_warning "Please edit $ENV_FILE and fill in real values for API keys, etc."
            read -p "Press Enter to continue after editing the file, or Ctrl+C to cancel..."
        else
            print_error "Environment file $ENV_FILE and template not found. Cannot proceed."
            return 1
        fi
    fi
    
    # Stop existing containers
    print_status "Stopping existing $ENV_NAME containers..."
    $DOCKER_COMPOSE -f "$COMPOSE_FILE" -p "$PROJECT_NAME" down 2>/dev/null || true
    
    # Build images
    print_status "Building $ENV_NAME images..."
    $DOCKER_COMPOSE -f "$COMPOSE_FILE" -p "$PROJECT_NAME" build --no-cache
    
    # Start services
    print_status "Starting $ENV_NAME services..."
    $DOCKER_COMPOSE -f "$COMPOSE_FILE" -p "$PROJECT_NAME" up -d
    
    # Wait for services to be ready
    print_status "Waiting for $ENV_NAME services to be ready..."
    sleep 10
    
    # Check service status
    print_status "Checking $ENV_NAME service status..."
    $DOCKER_COMPOSE -f "$COMPOSE_FILE" -p "$PROJECT_NAME" ps
    
    # Show logs for backend
    print_status "Backend logs (last 20 lines):"
    $DOCKER_COMPOSE -f "$COMPOSE_FILE" -p "$PROJECT_NAME" logs --tail=20 backend || true
    
    echo ""
    print_status "$ENV_NAME environment deployment complete!"
    echo ""
}

# Deploy to DEV environment
print_step "========================================="
print_step "DEPLOYING TO DEV ENVIRONMENT"
print_step "========================================="
deploy_environment "DEV" "docker-compose.dev.yml" "crane-dev" "config/dev.env"

# Wait a bit between deployments
sleep 5

# Deploy to UAT environment
print_step "========================================="
print_step "DEPLOYING TO UAT ENVIRONMENT"
print_step "========================================="
deploy_environment "UAT" "docker-compose.uat.yml" "crane-uat" "config/uat.env"

# Summary
echo ""
echo "========================================="
print_status "DEPLOYMENT SUMMARY"
echo "========================================="
echo ""
print_status "DEV Environment:"
echo "  - Frontend: http://localhost:3101"
echo "  - Backend: http://localhost:8104"
echo "  - Database: localhost:5534"
echo "  - Redis: localhost:6480"
echo "  - Adminer: http://localhost:8182"
echo ""
print_status "UAT Environment:"
echo "  - Frontend: http://localhost:3201"
echo "  - Backend: http://localhost:8204"
echo "  - Database: localhost:5634"
echo "  - Redis: localhost:6580"
echo "  - Adminer: http://localhost:8282"
echo ""
print_status "To view logs:"
echo "  DEV:  $DOCKER_COMPOSE -f docker-compose.dev.yml -p crane-dev logs -f"
echo "  UAT:  $DOCKER_COMPOSE -f docker-compose.uat.yml -p crane-uat logs -f"
echo ""
print_status "To stop environments:"
echo "  DEV:  $DOCKER_COMPOSE -f docker-compose.dev.yml -p crane-dev down"
echo "  UAT:  $DOCKER_COMPOSE -f docker-compose.uat.yml -p crane-uat down"
echo ""
print_status "Deployment to DEV and UAT environments completed successfully!"
echo ""

