#!/usr/bin/env python3
"""
Stripe Key Validator
Validates Stripe key configuration and environment matching
"""

import os
import sys
from pathlib import Path

# Colors for terminal output
class Colors:
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color

def detect_key_type(key: str) -> str:
    """Detect if key is test, live, or unknown"""
    if not key or key.startswith("replace-with"):
        return "placeholder"
    if key.startswith("pk_test_") or key.startswith("sk_test_"):
        return "test"
    if key.startswith("pk_live_") or key.startswith("sk_live_"):
        return "live"
    return "unknown"

def validate_environment_file(env_file: Path, env_name: str) -> tuple[bool, list]:
    """Validate an environment file for Stripe configuration"""
    issues = []
    
    if not env_file.exists():
        print(f"{Colors.RED}✗ Environment file not found: {env_file}{Colors.NC}")
        return False, ["File not found"]
    
    print(f"\n{Colors.BLUE}Validating {env_name} environment: {env_file}{Colors.NC}")
    
    # Read environment variables
    env_vars = {}
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key] = value
    
    # Check environment
    environment = env_vars.get('ENVIRONMENT', '').lower()
    if environment:
        print(f"  {Colors.GREEN}✓ ENVIRONMENT: {environment}{Colors.NC}")
    else:
        print(f"  {Colors.YELLOW}⚠ ENVIRONMENT variable not set{Colors.NC}")
    
    # Check Stripe keys
    publishable_key = env_vars.get('STRIPE_PUBLISHABLE_KEY', '')
    secret_key = env_vars.get('STRIPE_SECRET_KEY', '')
    webhook_secret = env_vars.get('STRIPE_WEBHOOK_SECRET', '')
    
    pub_mode = detect_key_type(publishable_key)
    sec_mode = detect_key_type(secret_key)
    
    # Validate publishable key
    if not publishable_key:
        print(f"  {Colors.RED}✗ STRIPE_PUBLISHABLE_KEY: Not configured{Colors.NC}")
        issues.append("Missing publishable key")
    elif pub_mode == "placeholder":
        print(f"  {Colors.YELLOW}⚠ STRIPE_PUBLISHABLE_KEY: Placeholder value{Colors.NC}")
    elif pub_mode == "test":
        print(f"  {Colors.GREEN}✓ STRIPE_PUBLISHABLE_KEY: Test key detected{Colors.NC}")
    elif pub_mode == "live":
        print(f"  {Colors.GREEN}✓ STRIPE_PUBLISHABLE_KEY: Live key detected{Colors.NC}")
    else:
        print(f"  {Colors.RED}✗ STRIPE_PUBLISHABLE_KEY: Invalid format{Colors.NC}")
        issues.append("Invalid publishable key format")
    
    # Validate secret key
    if not secret_key:
        print(f"  {Colors.RED}✗ STRIPE_SECRET_KEY: Not configured{Colors.NC}")
        issues.append("Missing secret key")
    elif sec_mode == "placeholder":
        print(f"  {Colors.YELLOW}⚠ STRIPE_SECRET_KEY: Placeholder value{Colors.NC}")
    elif sec_mode == "test":
        print(f"  {Colors.GREEN}✓ STRIPE_SECRET_KEY: Test key detected{Colors.NC}")
    elif sec_mode == "live":
        print(f"  {Colors.GREEN}✓ STRIPE_SECRET_KEY: Live key detected{Colors.NC}")
    else:
        print(f"  {Colors.RED}✗ STRIPE_SECRET_KEY: Invalid format{Colors.NC}")
        issues.append("Invalid secret key format")
    
    # Check for key type mismatch
    if pub_mode != sec_mode and pub_mode not in ["placeholder", "unknown"] and sec_mode not in ["placeholder", "unknown"]:
        print(f"  {Colors.RED}✗ CRITICAL: Key type mismatch!{Colors.NC}")
        print(f"     Publishable key is {pub_mode} but secret key is {sec_mode}")
        issues.append("Key type mismatch")
        return False, issues
    
    # Validate environment-key matching
    if environment == "prod":
        if pub_mode == "test" or sec_mode == "test":
            print(f"  {Colors.RED}✗ CRITICAL: Production environment is using TEST keys!{Colors.NC}")
            print(f"     Production MUST use live keys (pk_live_... and sk_live_...){Colors.NC}")
            issues.append("Production using test keys")
            return False, issues
        elif pub_mode == "live" and sec_mode == "live":
            print(f"  {Colors.GREEN}✓ Production environment using live keys (correct){Colors.NC}")
    elif environment in ["dev", "uat"]:
        if pub_mode == "live" or sec_mode == "live":
            print(f"  {Colors.RED}✗ CRITICAL: {environment.upper()} environment is using LIVE keys!{Colors.NC}")
            print(f"     {environment.upper()} environment should use test keys (pk_test_... and sk_test_...){Colors.NC}")
            issues.append(f"{environment.upper()} using live keys")
            return False, issues
        elif pub_mode == "test" and sec_mode == "test":
            print(f"  {Colors.GREEN}✓ {environment.upper()} environment using test keys (correct){Colors.NC}")
    
    # Check webhook secret
    if not webhook_secret:
        print(f"  {Colors.YELLOW}⚠ STRIPE_WEBHOOK_SECRET: Not configured{Colors.NC}")
    elif webhook_secret.startswith("whsec_"):
        print(f"  {Colors.GREEN}✓ STRIPE_WEBHOOK_SECRET: Configured{Colors.NC}")
    elif "replace-with" in webhook_secret:
        print(f"  {Colors.YELLOW}⚠ STRIPE_WEBHOOK_SECRET: Placeholder value{Colors.NC}")
    else:
        print(f"  {Colors.YELLOW}⚠ STRIPE_WEBHOOK_SECRET: Format may be incorrect (expected: whsec_...){Colors.NC}")
    
    return len(issues) == 0, issues

def main():
    script_dir = Path(__file__).parent.parent
    config_dir = script_dir / "config"
    
    print("=" * 50)
    print("Stripe Key Configuration Validator")
    print("=" * 50)
    
    all_valid = True
    total_issues = 0
    
    # Validate each environment
    env_files = [
        (config_dir / "dev.env", "DEV"),
        (config_dir / "uat.env", "UAT"),
        (config_dir / "prod.env.template", "PROD (template)"),
    ]
    
    # Check for actual prod.env
    prod_env = config_dir / "prod.env"
    if prod_env.exists():
        env_files.append((prod_env, "PROD"))
    else:
        print(f"\n{Colors.YELLOW}Note: config/prod.env not found (using template){Colors.NC}")
    
    for env_file, env_name in env_files:
        valid, issues = validate_environment_file(env_file, env_name)
        if not valid:
            all_valid = False
            total_issues += len(issues)
    
    # Summary
    print("\n" + "=" * 50)
    print("Validation Summary")
    print("=" * 50)
    
    if all_valid and total_issues == 0:
        print(f"{Colors.GREEN}✓ All Stripe configurations are valid{Colors.NC}")
        return 0
    else:
        print(f"{Colors.RED}✗ {total_issues} issue(s) found{Colors.NC}")
        print("\nPlease fix the issues above before deploying.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

