#!/bin/bash
# Script to test file uploads to DigitalOcean Spaces for each environment
# Verifies that files are stored in the correct environment-specific buckets

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
echo "File Upload Test - Environment Verification"
echo "=========================================="
echo ""

# Test endpoints
DEV_API="http://localhost:8104/api/v1"
UAT_API="http://localhost:8204/api/v1"
PROD_API="http://localhost:8004/api/v1"

# Create a test file (PDF format for service records upload)
TEST_FILE="/tmp/test-upload-$(date +%s).pdf"
# Create a minimal PDF file
cat > "$TEST_FILE" << 'PDFEOF'
%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
/Resources <<
/Font <<
/F1 <<
/Type /Font
/Subtype /Type1
/BaseFont /Helvetica
>>
>>
>>
>>
endobj
4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
100 700 Td
(Test Upload) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000306 00000 n
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
398
%%EOF
PDFEOF

echo -e "${BLUE}Test file created: $TEST_FILE${NC}"
echo ""

# Function to test upload to an environment
test_upload() {
    local env=$1
    local api_url=$2
    local expected_bucket=$3
    
    echo -e "${YELLOW}Testing $env environment...${NC}"
    echo "  API URL: $api_url"
    echo "  Expected bucket: $expected_bucket"
    
    # Check if backend is running
    local container_name=""
    if [ "$env" = "dev" ]; then
        container_name="crane-dev-backend-1"
    elif [ "$env" = "uat" ]; then
        container_name="crane-uat-backend-1"
    else
        container_name="crane-backend-1"
    fi
    
    if ! docker ps --format "{{.Names}}" | grep -q "^${container_name}$"; then
        echo -e "  ${RED}✗ Backend container not running: $container_name${NC}"
        echo ""
        return 1
    fi
    
    # Check if API is accessible
    if ! curl -s -f "$api_url/health" > /dev/null 2>&1; then
        echo -e "  ${RED}✗ API not accessible at $api_url${NC}"
        echo ""
        return 1
    fi
    
    # Upload test file
    echo "  Uploading test file..."
    local response=$(curl -s -X POST \
        -F "files=@$TEST_FILE" \
        "$api_url/fmv-reports/upload-service-records" 2>&1)
    
    if echo "$response" | grep -q "success.*true"; then
        echo -e "  ${GREEN}✓ File uploaded successfully${NC}"
        
        # Extract URL from response
        local file_url=$(echo "$response" | grep -o '"url":"[^"]*"' | head -1 | cut -d'"' -f4 || echo "")
        
        if [ -n "$file_url" ]; then
            echo "  File URL: $file_url"
            
            # Verify URL contains expected bucket
            if echo "$file_url" | grep -q "$expected_bucket"; then
                echo -e "  ${GREEN}✓ URL contains expected bucket: $expected_bucket${NC}"
            else
                echo -e "  ${YELLOW}⚠ URL does not contain expected bucket${NC}"
                echo "    Expected: $expected_bucket"
                echo "    Got: $file_url"
            fi
            
            # Verify URL contains environment prefix in path
            local env_lower=$(echo "$env" | tr '[:upper:]' '[:lower:]')
            if echo "$file_url" | grep -q "/${env_lower}/"; then
                echo -e "  ${GREEN}✓ URL contains environment prefix: /${env_lower}/${NC}"
            else
                echo -e "  ${YELLOW}⚠ URL does not contain environment prefix${NC}"
            fi
            
            # Test file accessibility
            echo "  Testing file accessibility..."
            if curl -s -f -I "$file_url" > /dev/null 2>&1; then
                echo -e "  ${GREEN}✓ File is accessible via CDN${NC}"
            else
                echo -e "  ${YELLOW}⚠ File may not be accessible yet (CDN propagation may take a few minutes)${NC}"
            fi
        else
            echo -e "  ${YELLOW}⚠ Could not extract file URL from response${NC}"
            echo "  Response: $response"
        fi
    else
        echo -e "  ${RED}✗ Upload failed${NC}"
        echo "  Response: $response"
        echo ""
        return 1
    fi
    
    echo ""
    return 0
}

# Test each environment
echo "Starting upload tests..."
echo ""

SUCCESS=true

# Test Dev
if [ -f "docker-compose.dev.yml" ]; then
    test_upload "dev" "$DEV_API" "crane-intelligence-storage-dev"
    if [ $? -ne 0 ]; then
        SUCCESS=false
    fi
else
    echo -e "${YELLOW}Skipping dev test (docker-compose.dev.yml not found)${NC}"
    echo ""
fi

# Test UAT
if [ -f "docker-compose.uat.yml" ]; then
    test_upload "uat" "$UAT_API" "crane-intelligence-storage-uat"
    if [ $? -ne 0 ]; then
        SUCCESS=false
    fi
else
    echo -e "${YELLOW}Skipping UAT test (docker-compose.uat.yml not found)${NC}"
    echo ""
fi

# Test Production
if [ -f "docker-compose.yml" ]; then
    test_upload "prod" "$PROD_API" "crane-intelligence-storage"
    if [ $? -ne 0 ]; then
        SUCCESS=false
    fi
else
    echo -e "${YELLOW}Skipping production test (docker-compose.yml not found)${NC}"
    echo ""
fi

# Cleanup
rm -f "$TEST_FILE"

# Summary
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo ""

if [ "$SUCCESS" = true ]; then
    echo -e "${GREEN}All upload tests completed!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Check DigitalOcean Spaces dashboard to verify files are in correct buckets:"
    echo "   https://cloud.digitalocean.com/spaces"
    echo ""
    echo "2. Verify folder structure:"
    echo "   - dev/service-records/"
    echo "   - uat/service-records/"
    echo "   - prod/service-records/"
    echo ""
    echo "3. Check that CDN is working for each bucket"
else
    echo -e "${YELLOW}Some tests failed. Please check the output above.${NC}"
    echo ""
    echo "Common issues:"
    echo "1. Backend containers not running - restart with: ./scripts/restart-backends-with-env-config.sh"
    echo "2. Buckets not created - create them in DigitalOcean dashboard or use: ./scripts/create-do-spaces-buckets.sh"
    echo "3. CDN not enabled - enable CDN in DigitalOcean dashboard for each bucket"
fi

echo ""

