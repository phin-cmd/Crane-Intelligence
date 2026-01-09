#!/usr/bin/env python3
"""Test script to diagnose DigitalOcean Spaces upload issues"""

import os
import sys
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.config import settings
from app.services.storage_service import get_storage_service

def test_storage_service():
    """Test if storage service is properly initialized"""
    print("=" * 80)
    print("Testing DigitalOcean Spaces Storage Service")
    print("=" * 80)
    
    # Check environment variables (storage service reads directly from os.getenv)
    import os
    print("\n1. Checking Environment Variables:")
    do_spaces_key = os.getenv("DO_SPACES_KEY")
    do_spaces_secret = os.getenv("DO_SPACES_SECRET")
    do_spaces_region = os.getenv("DO_SPACES_REGION", "atl1")
    do_spaces_bucket = os.getenv("DO_SPACES_BUCKET", "crane-intelligence-storage")
    environment = os.getenv("ENVIRONMENT", "prod")
    
    print(f"   DO_SPACES_KEY: {'SET' if do_spaces_key else 'NOT SET'} ({do_spaces_key[:10] + '...' if do_spaces_key else 'None'})")
    print(f"   DO_SPACES_SECRET: {'SET' if do_spaces_secret else 'NOT SET'} ({do_spaces_secret[:10] + '...' if do_spaces_secret else 'None'})")
    print(f"   DO_SPACES_REGION: {do_spaces_region}")
    print(f"   DO_SPACES_BUCKET: {do_spaces_bucket}")
    print(f"   ENVIRONMENT: {environment}")
    
    # Check storage service initialization
    print("\n2. Testing Storage Service Initialization:")
    try:
        storage_service = get_storage_service()
        if storage_service:
            print(f"   ✅ Storage service created")
            print(f"   S3 Client: {'Initialized' if storage_service.s3_client else 'NOT Initialized'}")
            print(f"   Bucket: {storage_service.bucket}")
            print(f"   Region: {storage_service.region}")
            print(f"   CDN Endpoint: {storage_service.cdn_endpoint}")
            
            # Test upload
            print("\n3. Testing File Upload:")
            test_content = b"Test file content for DigitalOcean Spaces upload"
            test_filename = "test-upload.txt"
            
            try:
                cdn_url = storage_service.upload_file(
                    file_content=test_content,
                    filename=test_filename,
                    folder="test-uploads",
                    content_type="text/plain"
                )
                print(f"   ✅ Upload successful!")
                print(f"   CDN URL: {cdn_url}")
                return True
            except Exception as upload_error:
                print(f"   ❌ Upload failed: {upload_error}")
                import traceback
                print(traceback.format_exc())
                return False
        else:
            print("   ❌ Storage service is None")
            return False
    except Exception as e:
        print(f"   ❌ Error initializing storage service: {e}")
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = test_storage_service()
    sys.exit(0 if success else 1)
