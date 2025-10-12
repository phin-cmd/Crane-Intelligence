#!/usr/bin/env python3
"""
Crane Intelligence - Automated Header Update Script
Updates all HTML files with unified authentication header
"""

import os
import re
import shutil
from pathlib import Path
from datetime import datetime

# Configuration
FRONTEND_DIR = Path("/root/Crane-Intelligence/frontend")
BACKUP_DIR = Path(f"/root/Crane-Intelligence/header_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")

# Files to exclude from update
EXCLUDE_FILES = ['index.html']  # React build file
EXCLUDE_DIRS = []  # Can add admin if needed

def create_backup():
    """Create backup of all HTML files"""
    print("Creating backup of all HTML files...")
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    html_files = list(FRONTEND_DIR.glob("**/*.html"))
    for html_file in html_files:
        relative_path = html_file.relative_to(FRONTEND_DIR)
        backup_file = BACKUP_DIR / relative_path
        backup_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(html_file, backup_file)
    
    print(f"✓ Backup created at: {BACKUP_DIR}\n")
    return len(html_files)

def should_skip_file(file_path):
    """Check if file should be skipped"""
    file_name = file_path.name
    
    # Skip excluded files
    if file_name in EXCLUDE_FILES:
        return True
    
    # Skip admin directory
    if 'admin' in str(file_path):
        return True
    
    return False

def has_unified_auth(content):
    """Check if file already has unified auth script"""
    return 'unified-auth.js' in content

def has_unified_header_css(content):
    """Check if file already has unified header CSS"""
    return 'unified-header.css' in content

def update_head_section(content):
    """Add unified auth and CSS to head section"""
    
    # Check if already has the scripts
    if has_unified_auth(content) and has_unified_header_css(content):
        return content, False
    
    # Find the closing head tag
    head_close_pattern = r'</head>'
    
    # Prepare the scripts to insert
    scripts_to_add = []
    
    if not has_unified_header_css(content):
        scripts_to_add.append('    <!-- Unified Header CSS -->\n    <link rel="stylesheet" href="/css/unified-header.css">\n')
    
    if not has_unified_auth(content):
        scripts_to_add.append('    <!-- Unified Authentication System -->\n    <script src="/js/unified-auth.js" defer></script>\n')
    
    if not scripts_to_add:
        return content, False
    
    # Insert before closing head tag
    insertion = ''.join(scripts_to_add) + '  '
    updated_content = re.sub(head_close_pattern, insertion + '</head>', content, count=1)
    
    return updated_content, True

def main():
    """Main execution function"""
    print("=" * 50)
    print("Crane Intelligence Header Update Script")
    print("=" * 50)
    print()
    
    # Create backup
    total_files = create_backup()
    
    # Find all HTML files
    html_files = list(FRONTEND_DIR.glob("**/*.html"))
    print(f"Found {len(html_files)} HTML files to process\n")
    
    # Track statistics
    updated_count = 0
    skipped_count = 0
    already_updated_count = 0
    error_count = 0
    
    print("Processing files...")
    print("-" * 50)
    
    for html_file in html_files:
        file_name = html_file.name
        
        # Skip certain files
        if should_skip_file(html_file):
            print(f"⊘ Skipping: {file_name}")
            skipped_count += 1
            continue
        
        try:
            # Read file content
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Update head section
            updated_content, was_updated = update_head_section(content)
            
            if was_updated:
                # Write updated content
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                print(f"✓ Updated: {file_name}")
                updated_count += 1
            else:
                print(f"○ Already has unified auth: {file_name}")
                already_updated_count += 1
                
        except Exception as e:
            print(f"✗ Error processing {file_name}: {e}")
            error_count += 1
    
    # Print summary
    print()
    print("=" * 50)
    print("Update Complete!")
    print("=" * 50)
    print(f"Total files found: {len(html_files)}")
    print(f"Files updated: {updated_count}")
    print(f"Already updated: {already_updated_count}")
    print(f"Files skipped: {skipped_count}")
    print(f"Errors: {error_count}")
    print(f"Backup location: {BACKUP_DIR}")
    print()
    
    print("Next steps:")
    print("1. Test the homepage: http://your-domain/homepage.html")
    print("2. Test login/logout flow")
    print("3. Check responsive design on mobile")
    print("4. If issues occur, restore from backup:")
    print(f"   cp -r {BACKUP_DIR}/* {FRONTEND_DIR}/")
    print()
    
    print("Manual header update required for:")
    print("- Add the header HTML structure to each page")
    print("- See HEADER_IMPLEMENTATION_GUIDE.md for details")
    print()

if __name__ == "__main__":
    main()

