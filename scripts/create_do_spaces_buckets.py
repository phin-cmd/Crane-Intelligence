#!/usr/bin/env python3
"""
Script to create DigitalOcean Spaces buckets using boto3
Uses credentials from environment configuration files
"""

import os
import sys
import json
from pathlib import Path

try:
    import boto3
    from botocore.exceptions import ClientError, BotoCoreError
    from botocore.config import Config
except ImportError:
    print("ERROR: boto3 is not installed.")
    print("Install it with: pip3 install boto3")
    sys.exit(1)

# Colors for terminal output
class Colors:
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color

def load_config():
    """Load DigitalOcean Spaces configuration from dev.env"""
    script_dir = Path(__file__).parent.parent
    config_file = script_dir / "config" / "dev.env"
    
    if not config_file.exists():
        print(f"{Colors.RED}ERROR: config/dev.env not found{Colors.NC}")
        sys.exit(1)
    
    config = {}
    with open(config_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                if key.startswith('DO_SPACES'):
                    config[key] = value
    
    required_keys = ['DO_SPACES_KEY', 'DO_SPACES_SECRET', 'DO_SPACES_REGION']
    for key in required_keys:
        if key not in config:
            print(f"{Colors.RED}ERROR: {key} not found in config/dev.env{Colors.NC}")
            sys.exit(1)
    
    return config

def create_spaces_client(config):
    """Create boto3 client for DigitalOcean Spaces"""
    region = config['DO_SPACES_REGION']
    endpoint = f"https://{region}.digitaloceanspaces.com"
    
    s3_config = Config(
        signature_version='s3v4',
        s3={
            'addressing_style': 'virtual'
        }
    )
    
    client = boto3.client(
        's3',
        endpoint_url=endpoint,
        aws_access_key_id=config['DO_SPACES_KEY'],
        aws_secret_access_key=config['DO_SPACES_SECRET'],
        region_name=region,
        config=s3_config
    )
    
    return client, region

def bucket_exists(client, bucket_name):
    """Check if bucket exists"""
    try:
        client.head_bucket(Bucket=bucket_name)
        return True
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            return False
        # Other errors (403, etc.) - assume bucket exists or permission issue
        return None

def create_bucket(client, bucket_name, region):
    """Create a DigitalOcean Spaces bucket"""
    try:
        # DigitalOcean Spaces uses region in the location constraint
        location = {'LocationConstraint': region}
        client.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration=location
        )
        return True, None
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'BucketAlreadyExists':
            return True, "already_exists"
        elif error_code == 'BucketAlreadyOwnedByYou':
            return True, "already_exists"
        else:
            return False, str(e)

def main():
    print("=" * 50)
    print("DigitalOcean Spaces Bucket Creation")
    print("=" * 50)
    print()
    
    # Load configuration
    config = load_config()
    region = config['DO_SPACES_REGION']
    
    print(f"{Colors.BLUE}Using region: {region}{Colors.NC}")
    print(f"{Colors.BLUE}Endpoint: https://{region}.digitaloceanspaces.com{Colors.NC}")
    print()
    
    # Create S3 client
    try:
        client, region = create_spaces_client(config)
    except Exception as e:
        print(f"{Colors.RED}ERROR: Failed to create Spaces client: {e}{Colors.NC}")
        sys.exit(1)
    
    # Buckets to create
    buckets = [
        "crane-intelligence-storage-dev",
        "crane-intelligence-storage-uat",
        "crane-intelligence-storage"
    ]
    
    success_count = 0
    total_count = len(buckets)
    
    for bucket_name in buckets:
        print(f"{Colors.YELLOW}Processing bucket: {bucket_name}{Colors.NC}")
        
        # Check if bucket exists
        exists = bucket_exists(client, bucket_name)
        
        if exists is True:
            print(f"  {Colors.GREEN}✓ Bucket already exists: {bucket_name}{Colors.NC}")
            success_count += 1
        elif exists is None:
            print(f"  {Colors.YELLOW}⚠ Could not verify bucket status (may be permission issue){Colors.NC}")
            print(f"  Attempting to create anyway...")
            success, message = create_bucket(client, bucket_name, region)
            if success:
                if message == "already_exists":
                    print(f"  {Colors.GREEN}✓ Bucket exists: {bucket_name}{Colors.NC}")
                else:
                    print(f"  {Colors.GREEN}✓ Bucket created: {bucket_name}{Colors.NC}")
                success_count += 1
            else:
                print(f"  {Colors.RED}✗ Failed to create bucket: {bucket_name}{Colors.NC}")
                print(f"    Error: {message}")
        else:
            # Bucket doesn't exist, create it
            success, message = create_bucket(client, bucket_name, region)
            if success:
                if message == "already_exists":
                    print(f"  {Colors.GREEN}✓ Bucket exists: {bucket_name}{Colors.NC}")
                else:
                    print(f"  {Colors.GREEN}✓ Bucket created: {bucket_name}{Colors.NC}")
                success_count += 1
            else:
                print(f"  {Colors.RED}✗ Failed to create bucket: {bucket_name}{Colors.NC}")
                print(f"    Error: {message}")
        
        print()
    
    # Summary
    print("=" * 50)
    print("Bucket Creation Summary")
    print("=" * 50)
    print()
    
    if success_count == total_count:
        print(f"{Colors.GREEN}All buckets processed successfully! ({success_count}/{total_count}){Colors.NC}")
    else:
        print(f"{Colors.YELLOW}Some buckets may have failed. ({success_count}/{total_count} succeeded){Colors.NC}")
    
    print()
    print("Next steps:")
    print("1. Enable CDN for each bucket in DigitalOcean dashboard:")
    print("   https://cloud.digitalocean.com/spaces")
    print()
    print("2. For each bucket:")
    print("   - Click on the bucket name")
    print("   - Go to 'Settings' tab")
    print("   - Enable 'CDN (Content Delivery Network)'")
    print("   - Verify the CDN endpoint matches your configuration")
    print()
    print("3. Verify CDN endpoints:")
    print(f"   - Dev: https://crane-intelligence-storage-dev.{region}.cdn.digitaloceanspaces.com")
    print(f"   - UAT: https://crane-intelligence-storage-uat.{region}.cdn.digitaloceanspaces.com")
    print(f"   - Prod: https://crane-intelligence-storage.{region}.cdn.digitaloceanspaces.com")
    print()
    print("4. Test file uploads using:")
    print("   ./scripts/test-file-uploads.sh")
    print()

if __name__ == "__main__":
    main()

