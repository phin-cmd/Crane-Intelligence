#!/bin/bash
# Script to create DigitalOcean Spaces buckets using S3-compatible API
# Uses the credentials from environment files

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
echo "DigitalOcean Spaces Bucket Creation (S3 API)"
echo "=========================================="
echo ""

# Load credentials from dev.env (they should be the same for all environments)
if [ -f "config/dev.env" ]; then
    source <(grep "^DO_SPACES" config/dev.env | sed 's/^/export /')
    REGION=${DO_SPACES_REGION:-atl1}
else
    echo -e "${RED}ERROR: config/dev.env not found${NC}"
    exit 1
fi

if [ -z "$DO_SPACES_KEY" ] || [ -z "$DO_SPACES_SECRET" ]; then
    echo -e "${RED}ERROR: DO_SPACES_KEY or DO_SPACES_SECRET not found in config/dev.env${NC}"
    exit 1
fi

ENDPOINT="https://${REGION}.digitaloceanspaces.com"

echo -e "${BLUE}Using region: $REGION${NC}"
echo -e "${BLUE}Endpoint: $ENDPOINT${NC}"
echo ""

# Check if awscli is available (for S3 API)
if ! command -v aws &> /dev/null; then
    echo -e "${YELLOW}awscli not found. Installing...${NC}"
    apt-get update -qq && apt-get install -y -qq awscli > /dev/null 2>&1 || {
        echo -e "${RED}Failed to install awscli. Please install manually:${NC}"
        echo "  apt-get update && apt-get install -y awscli"
        echo ""
        echo "Or create buckets manually in DigitalOcean dashboard:"
        echo "  https://cloud.digitalocean.com/spaces"
        exit 1
    }
fi

# Configure AWS CLI for DigitalOcean Spaces
export AWS_ACCESS_KEY_ID="$DO_SPACES_KEY"
export AWS_SECRET_ACCESS_KEY="$DO_SPACES_SECRET"
export AWS_DEFAULT_REGION="$REGION"

# Buckets to create
BUCKETS=(
    "crane-intelligence-storage-dev"
    "crane-intelligence-storage-uat"
    "crane-intelligence-storage"
)

# Function to create a bucket
create_bucket() {
    local bucket_name=$1
    
    echo -e "${YELLOW}Creating bucket: $bucket_name${NC}"
    
    # Check if bucket already exists
    if aws s3 ls "s3://${bucket_name}" --endpoint-url "$ENDPOINT" 2>/dev/null; then
        echo -e "  ${GREEN}✓ Bucket already exists: $bucket_name${NC}"
        return 0
    fi
    
    # Create the bucket
    if aws s3 mb "s3://${bucket_name}" \
        --endpoint-url "$ENDPOINT" \
        --region "$REGION" 2>/dev/null; then
        echo -e "  ${GREEN}✓ Bucket created: $bucket_name${NC}"
        
        # Set public read access for CDN (create bucket policy)
        echo "  Setting up public read access for CDN..."
        cat > /tmp/bucket-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::${bucket_name}/*"
    }
  ]
}
EOF
        
        # Note: DigitalOcean Spaces uses different policy format
        # The public access is typically set via the dashboard
        echo -e "  ${YELLOW}⚠ Please enable CDN and set public read access in DigitalOcean dashboard${NC}"
        echo "     URL: https://cloud.digitalocean.com/spaces"
        
        rm -f /tmp/bucket-policy.json
        return 0
    else
        echo -e "  ${RED}✗ Failed to create bucket: $bucket_name${NC}"
        echo "  This might be because:"
        echo "    1. Bucket name is already taken globally"
        echo "    2. Insufficient permissions"
        echo "    3. Network connectivity issues"
        return 1
    fi
}

# Create all buckets
SUCCESS=true
for bucket in "${BUCKETS[@]}"; do
    create_bucket "$bucket"
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
echo "2. For each bucket:"
echo "   - Click on the bucket name"
echo "   - Go to 'Settings' tab"
echo "   - Enable 'CDN (Content Delivery Network)'"
echo "   - Verify the CDN endpoint matches your configuration"
echo ""
echo "3. Verify CDN endpoints:"
echo "   - Dev: https://crane-intelligence-storage-dev.${REGION}.cdn.digitaloceanspaces.com"
echo "   - UAT: https://crane-intelligence-storage-uat.${REGION}.cdn.digitaloceanspaces.com"
echo "   - Prod: https://crane-intelligence-storage.${REGION}.cdn.digitaloceanspaces.com"
echo ""
echo "4. Test file uploads using:"
echo "   ./scripts/test-file-uploads.sh"
echo ""

