#!/bin/bash
# Script to create DigitalOcean Spaces buckets using doctl CLI
# Prerequisites: doctl must be installed and authenticated

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CRANE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$CRANE_DIR"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "=========================================="
echo "DigitalOcean Spaces Bucket Creation"
echo "=========================================="
echo ""

# Check if doctl is installed
if ! command -v doctl &> /dev/null; then
    echo -e "${RED}ERROR: doctl (DigitalOcean CLI) is not installed.${NC}"
    echo ""
    echo "To install doctl:"
    echo "  1. Download from: https://docs.digitalocean.com/reference/doctl/how-to/install/"
    echo "  2. Or use: snap install doctl"
    echo "  3. Authenticate: doctl auth init"
    echo ""
    echo "Alternatively, create buckets manually in the DigitalOcean dashboard:"
    echo "  https://cloud.digitalocean.com/spaces"
    echo ""
    exit 1
fi

# Check if doctl is authenticated
if ! doctl auth list &> /dev/null; then
    echo -e "${RED}ERROR: doctl is not authenticated.${NC}"
    echo "Run: doctl auth init"
    exit 1
fi

# Get region from config (default to atl1)
REGION=${DO_SPACES_REGION:-atl1}
if [ -f "config/dev.env" ]; then
    REGION=$(grep "DO_SPACES_REGION" config/dev.env | cut -d'=' -f2 | tr -d ' ' || echo "atl1")
fi

echo -e "${BLUE}Using region: $REGION${NC}"
echo ""

# Buckets to create
BUCKETS=(
    "crane-intelligence-storage-dev"
    "crane-intelligence-storage-uat"
    "crane-intelligence-storage"
)

# Function to create a bucket
create_bucket() {
    local bucket_name=$1
    local is_public=$2
    
    echo -e "${YELLOW}Creating bucket: $bucket_name${NC}"
    
    # Check if bucket already exists
    if doctl spaces list --region "$REGION" --format Name | grep -q "^${bucket_name}$"; then
        echo -e "  ${GREEN}✓ Bucket already exists: $bucket_name${NC}"
        return 0
    fi
    
    # Create the bucket
    if doctl spaces create "$bucket_name" --region "$REGION"; then
        echo -e "  ${GREEN}✓ Bucket created: $bucket_name${NC}"
        
        # Set public access if needed (for CDN)
        if [ "$is_public" = "true" ]; then
            echo "  Setting public read access for CDN..."
            # Note: This requires additional configuration via DigitalOcean dashboard
            echo -e "  ${YELLOW}⚠ Please enable CDN and set public read access in DigitalOcean dashboard${NC}"
        fi
        
        return 0
    else
        echo -e "  ${RED}✗ Failed to create bucket: $bucket_name${NC}"
        return 1
    fi
}

# Create all buckets
SUCCESS=true
for bucket in "${BUCKETS[@]}"; do
    create_bucket "$bucket" "true"
    if [ $? -ne 0 ]; then
        SUCCESS=false
    fi
    echo ""
done

# Summary
echo "=========================================="
echo "Bucket Creation Summary"
echo "=========================================="
echo ""

if [ "$SUCCESS" = true ]; then
    echo -e "${GREEN}All buckets processed successfully!${NC}"
else
    echo -e "${YELLOW}Some buckets may have failed. Please check the output above.${NC}"
fi

echo ""
echo "Next steps:"
echo "1. Enable CDN for each bucket in DigitalOcean dashboard:"
echo "   https://cloud.digitalocean.com/spaces"
echo ""
echo "2. Verify CDN endpoints match your configuration:"
echo "   - Dev: https://crane-intelligence-storage-dev.${REGION}.cdn.digitaloceanspaces.com"
echo "   - UAT: https://crane-intelligence-storage-uat.${REGION}.cdn.digitaloceanspaces.com"
echo "   - Prod: https://crane-intelligence-storage.${REGION}.cdn.digitaloceanspaces.com"
echo ""
echo "3. Test file uploads using:"
echo "   ./scripts/test-file-uploads.sh"
echo ""

