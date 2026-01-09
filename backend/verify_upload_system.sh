#!/bin/bash
# Comprehensive script to verify file upload system

echo "=========================================="
echo "DigitalOcean Spaces Upload System Check"
echo "=========================================="
echo ""

# Step 1: Check environment variables
echo "1. Checking Environment Variables..."
echo "-----------------------------------"
if [ -f /root/crane/backend/.env ]; then
    echo "✅ .env file exists"
    if grep -q "DO_SPACES_KEY" /root/crane/backend/.env; then
        echo "✅ DO_SPACES_KEY is set"
    else
        echo "⚠️  DO_SPACES_KEY not found in .env (will use fallback)"
    fi
    if grep -q "DO_SPACES_SECRET" /root/crane/backend/.env; then
        echo "✅ DO_SPACES_SECRET is set"
    else
        echo "⚠️  DO_SPACES_SECRET not found in .env (will use fallback)"
    fi
    if grep -q "DO_SPACES_REGION" /root/crane/backend/.env; then
        REGION=$(grep "DO_SPACES_REGION" /root/crane/backend/.env | cut -d'=' -f2)
        echo "✅ DO_SPACES_REGION: $REGION"
    else
        echo "⚠️  DO_SPACES_REGION not found (will use default: atl1)"
    fi
    if grep -q "DO_SPACES_BUCKET" /root/crane/backend/.env; then
        BUCKET=$(grep "DO_SPACES_BUCKET" /root/crane/backend/.env | cut -d'=' -f2)
        echo "✅ DO_SPACES_BUCKET: $BUCKET"
    else
        echo "⚠️  DO_SPACES_BUCKET not found (will use default: crane-intelligence-storage)"
    fi
else
    echo "❌ .env file not found"
fi
echo ""

# Step 2: Check Python dependencies
echo "2. Checking Python Dependencies..."
echo "-----------------------------------"
cd /root/crane/backend
python3 -c "import boto3; print('✅ boto3 installed')" 2>&1 || echo "❌ boto3 not installed"
python3 -c "from botocore.exceptions import ClientError; print('✅ botocore installed')" 2>&1 || echo "❌ botocore not installed"
echo ""

# Step 3: Test storage service initialization
echo "3. Testing Storage Service Initialization..."
echo "-----------------------------------"
python3 -c "
import sys
sys.path.insert(0, '.')
try:
    from app.services.storage_service import get_storage_service
    storage = get_storage_service()
    if storage:
        print('✅ Storage service created')
        if storage.s3_client:
            print('✅ s3_client initialized')
            print(f'   Bucket: {storage.bucket}')
            print(f'   Region: {storage.region}')
            print(f'   Environment: {storage.environment}')
            print(f'   CDN Endpoint: {storage.cdn_endpoint}')
        else:
            print('❌ s3_client is None')
            print('   Check DO_SPACES_KEY and DO_SPACES_SECRET')
    else:
        print('❌ Storage service is None')
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
" 2>&1
echo ""

# Step 4: Test file upload
echo "4. Testing File Upload..."
echo "-----------------------------------"
python3 test_storage_upload.py 2>&1
echo ""

# Step 5: Check backend process
echo "5. Checking Backend Process..."
echo "-----------------------------------"
if pgrep -f "uvicorn.*main:app" > /dev/null; then
    echo "✅ Backend process is running"
    ps aux | grep -E "uvicorn.*main:app" | grep -v grep | head -1
else
    echo "⚠️  Backend process not found"
    echo "   To start: cd /root/crane/backend && bash start_backend.sh"
fi
echo ""

# Step 6: Check if backend is responding
echo "6. Checking Backend Health..."
echo "-----------------------------------"
if curl -s http://localhost:8004/health > /dev/null 2>&1; then
    echo "✅ Backend is responding on port 8004"
else
    echo "⚠️  Backend not responding on port 8004"
fi
echo ""

echo "=========================================="
echo "Check Complete"
echo "=========================================="
