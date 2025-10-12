#!/usr/bin/env python3
"""
Add auto-init-auth.js script to all pages that don't have it
This ensures authentication is properly initialized on every page load
"""

import os
import re
from pathlib import Path

FRONTEND_DIR = Path("/root/Crane-Intelligence/frontend")

def add_auto_init_script(file_path):
    """Add auto-init-auth.js script before closing body tag"""
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if already has the script
        if 'auto-init-auth.js' in content:
            return False, "Already has auto-init script"
        
        # Find the closing body tag
        body_close_pattern = r'(</body>)'
        
        if not re.search(body_close_pattern, content):
            return False, "No closing body tag found"
        
        # Insert the script before closing body tag
        script_tag = '    <script src="/js/auto-init-auth.js"></script>\n'
        
        content = re.sub(body_close_pattern, script_tag + r'\1', content)
        
        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True, "Added auto-init script"
        
    except Exception as e:
        return False, f"Error: {e}"

def main():
    """Main execution"""
    print("=" * 70)
    print("Adding Auto-Init Auth Script to All Pages")
    print("=" * 70)
    print()
    
    # Get all HTML files
    html_files = list(FRONTEND_DIR.glob("*.html"))
    
    added_count = 0
    skipped_count = 0
    
    for html_file in html_files:
        file_name = html_file.name
        
        # Skip certain files
        if file_name in ['index.html', 'unified-header.html']:
            print(f"⊘ {file_name} - Skipped (excluded)")
            skipped_count += 1
            continue
        
        # Skip admin files
        if 'admin' in str(html_file):
            print(f"⊘ {file_name} - Skipped (admin)")
            skipped_count += 1
            continue
        
        success, message = add_auto_init_script(html_file)
        
        if success:
            print(f"✓ {file_name} - {message}")
            added_count += 1
        else:
            print(f"○ {file_name} - {message}")
            skipped_count += 1
    
    print()
    print("=" * 70)
    print(f"Complete! Added to: {added_count} pages | Skipped: {skipped_count}")
    print("=" * 70)
    print()
    print("The auto-init-auth.js script will now:")
    print("- Automatically initialize authentication on page load")
    print("- Update header with real user data")
    print("- Work consistently across all pages")

if __name__ == "__main__":
    main()

