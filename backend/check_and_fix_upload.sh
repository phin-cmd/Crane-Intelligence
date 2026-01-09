#!/bin/bash
# Script to check and fix file upload issues

echo "=== Checking DigitalOcean Spaces Configuration ==="
echo ""

# Check .env file
if [ -f /root/crane/backend/.env ]; then
    echo "✅ .env file exists"
    echo ""
    echo "DigitalOcean Spaces variables:"
    grep -E "DO_SPACES|ENVIRONMENT" /root/crane/backend/.env | sed 's/=.*/=***HIDDEN***/'
else
    echo "❌ .env file not found"
fi

echo ""
echo "=== Checking Storage Service Code ==="
echo ""

# Check if storage service file exists
if [ -f /root/crane/backend/app/services/storage_service.py ]; then
    echo "✅ storage_service.py exists"
    
    # Check for key functions
    if grep -q "def upload_file" /root/crane/backend/app/services/storage_service.py; then
        echo "✅ upload_file method found"
    else
        echo "❌ upload_file method NOT found"
    fi
    
    if grep -q "def get_storage_service" /root/crane/backend/app/services/storage_service.py; then
        echo "✅ get_storage_service function found"
    else
        echo "❌ get_storage_service function NOT found"
    fi
    
    # Check for boto3
    if grep -q "import boto3\|from boto3" /root/crane/backend/app/services/storage_service.py; then
        echo "✅ boto3 import found"
    else
        echo "❌ boto3 import NOT found"
    fi
    
    # Check for CDN endpoint
    if grep -q "cdn_endpoint\|digitaloceanspaces.com" /root/crane/backend/app/services/storage_service.py; then
        echo "✅ CDN endpoint found"
    else
        echo "❌ CDN endpoint NOT found"
    fi
else
    echo "❌ storage_service.py NOT found"
fi

echo ""
echo "=== Checking Upload Endpoints ==="
echo ""

# Check upload endpoints
if [ -f /root/crane/backend/app/api/v1/fmv_reports.py ]; then
    echo "✅ fmv_reports.py exists"
    
    if grep -q "upload-service-records" /root/crane/backend/app/api/v1/fmv_reports.py; then
        echo "✅ upload-service-records endpoint found"
    else
        echo "❌ upload-service-records endpoint NOT found"
    fi
    
    if grep -q "upload-bulk-file" /root/crane/backend/app/api/v1/fmv_reports.py; then
        echo "✅ upload-bulk-file endpoint found"
    else
        echo "❌ upload-bulk-file endpoint NOT found"
    fi
    
    if grep -q "get_storage_service" /root/crane/backend/app/api/v1/fmv_reports.py; then
        echo "✅ get_storage_service called in endpoints"
    else
        echo "❌ get_storage_service NOT called in endpoints"
    fi
else
    echo "❌ fmv_reports.py NOT found"
fi

echo ""
echo "=== Summary ==="
echo "If any ❌ errors above, those need to be fixed."
