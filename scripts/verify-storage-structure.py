#!/usr/bin/env python3
"""
Script to verify file storage structure in DigitalOcean Spaces
Checks that files are in correct buckets with correct folder structure
"""

import os
import sys
from pathlib import Path

try:
    import boto3
    from botocore.exceptions import ClientError, BotoCoreError
    from botocore.config import Config
except ImportError:
    print("ERROR: boto3 is not installed.")
    sys.exit(1)

# Colors for terminal output
class Colors:
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
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

def list_bucket_files(client, bucket_name, prefix=""):
    """List files in a bucket with a given prefix"""
    try:
        response = client.list_objects_v2(
            Bucket=bucket_name,
            Prefix=prefix,
            MaxKeys=100
        )
        
        files = []
        if 'Contents' in response:
            for obj in response['Contents']:
                files.append({
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'modified': obj['LastModified']
                })
        
        return files
    except ClientError as e:
        print(f"{Colors.RED}Error listing files: {e}{Colors.NC}")
        return []

def verify_environment_structure(client, bucket_name, environment):
    """Verify files are stored with correct environment prefix"""
    print(f"\n{Colors.CYAN}Verifying {environment.upper()} environment: {bucket_name}{Colors.NC}")
    print("-" * 60)
    
    # Check for environment-specific folders
    env_prefix = f"{environment}/"
    folders = {
        'service-records': f"{env_prefix}service-records/",
        'bulk-processing': f"{env_prefix}bulk-processing/",
        'fmv-reports': f"{env_prefix}fmv-reports/"
    }
    
    total_files = 0
    for folder_name, folder_path in folders.items():
        files = list_bucket_files(client, bucket_name, folder_path)
        file_count = len(files)
        total_files += file_count
        
        if file_count > 0:
            print(f"  {Colors.GREEN}✓{Colors.NC} {folder_name}: {file_count} file(s)")
            # Show first few files as examples
            for file_info in files[:3]:
                print(f"      - {file_info['key']}")
            if file_count > 3:
                print(f"      ... and {file_count - 3} more")
        else:
            print(f"  {Colors.YELLOW}○{Colors.NC} {folder_name}: No files yet")
    
    # Check for files without environment prefix (should not exist)
    all_files = list_bucket_files(client, bucket_name)
    incorrect_files = [f for f in all_files if not f['key'].startswith(env_prefix)]
    
    if incorrect_files:
        print(f"\n  {Colors.RED}⚠ Warning: Found files without environment prefix:{Colors.NC}")
        for file_info in incorrect_files[:5]:
            print(f"      - {file_info['key']}")
    else:
        print(f"\n  {Colors.GREEN}✓ All files have correct environment prefix{Colors.NC}")
    
    print(f"\n  Total files in {environment}: {total_files}")
    return total_files, len(incorrect_files) == 0

def test_cdn_accessibility(cdn_url):
    """Test if a CDN URL is accessible"""
    import urllib.request
    try:
        req = urllib.request.Request(cdn_url)
        req.add_header('User-Agent', 'Mozilla/5.0')
        with urllib.request.urlopen(req, timeout=5) as response:
            return response.status == 200
    except:
        return False

def main():
    print("=" * 60)
    print("DigitalOcean Spaces - Storage Structure Verification")
    print("=" * 60)
    
    # Load configuration
    config = load_config()
    region = config['DO_SPACES_REGION']
    
    print(f"\n{Colors.BLUE}Region: {region}{Colors.NC}")
    print(f"{Colors.BLUE}Endpoint: https://{region}.digitaloceanspaces.com{Colors.NC}")
    
    # Create S3 client
    try:
        client, region = create_spaces_client(config)
    except Exception as e:
        print(f"{Colors.RED}ERROR: Failed to create Spaces client: {e}{Colors.NC}")
        sys.exit(1)
    
    # Environments to verify
    environments = [
        ('dev', 'crane-intelligence-storage-dev'),
        ('uat', 'crane-intelligence-storage-uat'),
        ('prod', 'crane-intelligence-storage')
    ]
    
    results = {}
    
    for env_name, bucket_name in environments:
        # Check if bucket exists
        try:
            client.head_bucket(Bucket=bucket_name)
        except ClientError as e:
            print(f"\n{Colors.RED}✗ Bucket not found or not accessible: {bucket_name}{Colors.NC}")
            print(f"  Error: {e}")
            results[env_name] = {'exists': False}
            continue
        
        results[env_name] = {'exists': True}
        
        # Verify structure
        total_files, correct_structure = verify_environment_structure(client, bucket_name, env_name)
        results[env_name]['files'] = total_files
        results[env_name]['correct_structure'] = correct_structure
        
        # Test CDN endpoint
        cdn_endpoint = f"https://{bucket_name}.{region}.cdn.digitaloceanspaces.com"
        print(f"\n  CDN Endpoint: {cdn_endpoint}")
        
        # Try to access a test file if any exist
        test_files = list_bucket_files(client, bucket_name, f"{env_name}/service-records/")
        if test_files:
            test_file_key = test_files[0]['key']
            test_cdn_url = f"{cdn_endpoint}/{test_file_key}"
            print(f"  Testing CDN: {test_cdn_url[:80]}...")
            
            if test_cdn_accessibility(test_cdn_url):
                print(f"  {Colors.GREEN}✓ CDN is accessible{Colors.NC}")
                results[env_name]['cdn_working'] = True
            else:
                print(f"  {Colors.YELLOW}⚠ CDN may not be fully configured yet{Colors.NC}")
                results[env_name]['cdn_working'] = False
        else:
            print(f"  {Colors.YELLOW}○ No files to test CDN (upload a file first){Colors.NC}")
            results[env_name]['cdn_working'] = None
    
    # Summary
    print("\n" + "=" * 60)
    print("Verification Summary")
    print("=" * 60)
    
    for env_name, result in results.items():
        if not result.get('exists'):
            print(f"\n{Colors.RED}{env_name.upper()}: Bucket not accessible{Colors.NC}")
            continue
        
        print(f"\n{Colors.CYAN}{env_name.upper()} Environment:{Colors.NC}")
        print(f"  Bucket: {environments[[e[0] for e in environments].index(env_name)][1]}")
        print(f"  Files: {result.get('files', 0)}")
        
        if result.get('correct_structure'):
            print(f"  Structure: {Colors.GREEN}✓ Correct{Colors.NC}")
        else:
            print(f"  Structure: {Colors.RED}✗ Issues found{Colors.NC}")
        
        cdn_status = result.get('cdn_working')
        if cdn_status is True:
            print(f"  CDN: {Colors.GREEN}✓ Working{Colors.NC}")
        elif cdn_status is False:
            print(f"  CDN: {Colors.YELLOW}⚠ Not accessible (may need time to propagate){Colors.NC}")
        else:
            print(f"  CDN: {Colors.YELLOW}○ Not tested (no files){Colors.NC}")
    
    print("\n" + "=" * 60)
    print("Verification Complete")
    print("=" * 60)
    print()

if __name__ == "__main__":
    main()

