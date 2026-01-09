#!/usr/bin/env python3
"""Script to fix and verify DigitalOcean Spaces storage service"""

import os
import sys

# Read the storage_service.py file
storage_file = '/root/crane/backend/app/services/storage_service.py'

try:
    with open(storage_file, 'r') as f:
        content = f.read()
    
    # Check for common issues
    issues = []
    
    # Check 1: Is s3_client initialized?
    if 'self.s3_client = None' in content and 'if not self.s3_client:' not in content:
        issues.append("s3_client might not be initialized")
    
    # Check 2: Are credentials checked?
    if 'DO_SPACES_KEY' not in content or 'DO_SPACES_SECRET' not in content:
        issues.append("DO_SPACES credentials not checked in storage service")
    
    # Check 3: Is upload_file method present?
    if 'def upload_file' not in content:
        issues.append("upload_file method missing")
    
    # Check 4: Is error handling present?
    if 'except' not in content or 'ClientError' not in content:
        issues.append("Error handling might be missing")
    
    print("Storage Service Analysis:")
    print("=" * 80)
    if issues:
        for issue in issues:
            print(f"⚠️  {issue}")
    else:
        print("✅ No obvious issues found in code structure")
    
    # Check if get_storage_service function exists
    if 'def get_storage_service' not in content:
        print("⚠️  get_storage_service function might be missing")
    else:
        print("✅ get_storage_service function found")
    
    # Check for CDN endpoint
    if 'cdn_endpoint' in content:
        print("✅ CDN endpoint found")
    else:
        print("⚠️  CDN endpoint might be missing")
        
except Exception as e:
    print(f"Error reading storage service file: {e}")
