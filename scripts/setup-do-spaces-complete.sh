#!/bin/bash
# Complete setup script for DigitalOcean Spaces environment separation
# This script guides through the entire setup process

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CRANE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$CRANE_DIR"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo "=========================================="
echo "DigitalOcean Spaces - Complete Setup"
echo "=========================================="
echo ""

# Step 1: Create buckets
echo -e "${CYAN}Step 1: Creating DigitalOcean Spaces Buckets${NC}"
echo ""

if command -v doctl &> /dev/null; then
    echo "Using doctl to create buckets..."
    ./scripts/create-do-spaces-buckets.sh
else
    echo -e "${YELLOW}doctl not found. Please create buckets manually:${NC}"
    echo ""
    echo "1. Go to DigitalOcean Dashboard: https://cloud.digitalocean.com/spaces"
    echo "2. Click 'Create a Space'"
    echo "3. Create the following buckets:"
    echo "   - crane-intelligence-storage-dev"
    echo "   - crane-intelligence-storage-uat"
    echo "   - crane-intelligence-storage"
    echo "4. Region: atl1 (or your configured region)"
    echo "5. Click 'Create a Space' for each"
    echo ""
    read -p "Press Enter when all buckets are created..."
fi

echo ""
echo -e "${CYAN}Step 2: Enable CDN for Each Bucket${NC}"
echo ""

echo "For each bucket, you need to enable CDN:"
echo ""
echo "1. Go to: https://cloud.digitalocean.com/spaces"
echo "2. Click on each bucket"
echo "3. Go to 'Settings' tab"
echo "4. Enable 'CDN (Content Delivery Network)'"
echo "5. Note the CDN endpoint (should match your config)"
echo ""
echo "Expected CDN endpoints:"
echo "  - Dev: https://crane-intelligence-storage-dev.atl1.cdn.digitaloceanspaces.com"
echo "  - UAT: https://crane-intelligence-storage-uat.atl1.cdn.digitaloceanspaces.com"
echo "  - Prod: https://crane-intelligence-storage.atl1.cdn.digitaloceanspaces.com"
echo ""
read -p "Press Enter when CDN is enabled for all buckets..."

echo ""
echo -e "${CYAN}Step 3: Restart Backend Services${NC}"
echo ""

echo "Restarting backend services with new configuration..."
./scripts/restart-backends-with-env-config.sh

echo ""
echo -e "${CYAN}Step 4: Test File Uploads${NC}"
echo ""

echo "Testing file uploads to verify everything is working..."
echo ""
read -p "Press Enter to start upload tests..."

./scripts/test-file-uploads.sh

echo ""
echo "=========================================="
echo -e "${GREEN}Setup Complete!${NC}"
echo "=========================================="
echo ""
echo "Your DigitalOcean Spaces are now configured with environment separation:"
echo ""
echo "  Dev:    crane-intelligence-storage-dev"
echo "  UAT:    crane-intelligence-storage-uat"
echo "  Prod:   crane-intelligence-storage"
echo ""
echo "Files will be organized as:"
echo "  {environment}/{folder}/{filename}"
echo ""
echo "Example:"
echo "  dev/service-records/abc123_file.pdf"
echo "  uat/service-records/def456_file.pdf"
echo "  prod/service-records/ghi789_file.pdf"
echo ""

