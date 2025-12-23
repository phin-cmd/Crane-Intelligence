#!/bin/bash
set -e

echo "=== Production Deployment Script ==="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="/root/crane"
FRONTEND_FILES=("report-generation.html" "dashboard.html")
BACKEND_FILE="backend/app/api/v1/fmv_reports.py"
ENV_FILE="backend/.env"

# Detect production paths
WEB_ROOT=""
if [ -d "/var/www/html" ]; then
    WEB_ROOT="/var/www/html"
elif [ -d "/var/www" ]; then
    WEB_ROOT="/var/www"
elif [ -d "/usr/share/nginx/html" ]; then
    WEB_ROOT="/usr/share/nginx/html"
else
    echo -e "${RED}Could not detect web root. Please specify WEB_ROOT manually.${NC}"
    exit 1
fi

echo -e "${GREEN}Detected web root: $WEB_ROOT${NC}"
echo ""

# Deploy frontend files
echo -e "${YELLOW}Step 1: Deploying frontend files...${NC}"
for file in "${FRONTEND_FILES[@]}"; do
    if [ -f "$PROJECT_ROOT/$file" ]; then
        echo "  Copying $file..."
        cp "$PROJECT_ROOT/$file" "$WEB_ROOT/$file"
        echo -e "  ${GREEN}✓${NC} $file deployed"
    else
        echo -e "  ${RED}✗${NC} $file not found"
    fi
done

# Deploy backend file (assuming backend is in /root/crane/backend or similar)
echo ""
echo -e "${YELLOW}Step 2: Deploying backend file...${NC}"
BACKEND_DIR="/root/crane/backend"
if [ -f "$PROJECT_ROOT/$BACKEND_FILE" ]; then
    echo "  Copying $BACKEND_FILE..."
    mkdir -p "$BACKEND_DIR/app/api/v1"
    cp "$PROJECT_ROOT/$BACKEND_FILE" "$BACKEND_DIR/app/api/v1/fmv_reports.py"
    echo -e "  ${GREEN}✓${NC} $BACKEND_FILE deployed"
else
    echo -e "  ${RED}✗${NC} $BACKEND_FILE not found"
fi

# Update .env file
echo ""
echo -e "${YELLOW}Step 3: Updating backend .env...${NC}"
if [ -f "$PROJECT_ROOT/$ENV_FILE" ]; then
    echo "  Updating $ENV_FILE..."
    # Backup existing .env
    if [ -f "$BACKEND_DIR/.env" ]; then
        cp "$BACKEND_DIR/.env" "$BACKEND_DIR/.env.backup.$(date +%Y%m%d_%H%M%S)"
    fi
    # Copy new .env
    cp "$PROJECT_ROOT/$ENV_FILE" "$BACKEND_DIR/.env"
    echo -e "  ${GREEN}✓${NC} .env updated"
else
    echo -e "  ${RED}✗${NC} $ENV_FILE not found"
fi

echo ""
echo -e "${GREEN}=== Deployment Complete ===${NC}"
echo ""
echo -e "${YELLOW}⚠️  IMPORTANT: Restart backend server for .env changes to take effect${NC}"
echo ""
echo "Next steps:"
echo "1. Restart backend server"
echo "2. Clear browser cache (Ctrl+Shift+R)"
echo "3. Test the complete flow"
