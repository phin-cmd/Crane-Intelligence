#!/bin/bash

###############################################################################
# CRANE INTELLIGENCE - AUTOMATIC HEADER UPDATE SCRIPT
# This script updates all HTML files with the unified authentication header
###############################################################################

set -e

echo "=========================================="
echo "Crane Intelligence Header Update Script"
echo "=========================================="
echo ""

# Define paths
FRONTEND_DIR="/root/Crane-Intelligence/frontend"
BACKUP_DIR="/root/Crane-Intelligence/header_backup_$(date +%Y%m%d_%H%M%S)"

# Create backup directory
echo "Creating backup of all HTML files..."
mkdir -p "$BACKUP_DIR"

# Find and backup all HTML files
find "$FRONTEND_DIR" -name "*.html" -type f | while read file; do
    relative_path="${file#$FRONTEND_DIR/}"
    backup_file="$BACKUP_DIR/$relative_path"
    mkdir -p "$(dirname "$backup_file")"
    cp "$file" "$backup_file"
done

echo "✓ Backup created at: $BACKUP_DIR"
echo ""

# Count total files
total_files=$(find "$FRONTEND_DIR" -name "*.html" -type f | wc -l)
echo "Found $total_files HTML files to update"
echo ""

# Function to check if unified-auth.js is already included
has_unified_auth() {
    grep -q "unified-auth.js" "$1"
}

# Function to check if unified-header.css is already included
has_unified_header_css() {
    grep -q "unified-header.css" "$1"
}

# Update counter
updated_count=0
skipped_count=0

echo "Processing files..."
echo "-------------------"

# Process each HTML file
find "$FRONTEND_DIR" -name "*.html" -type f | while read html_file; do
    filename=$(basename "$html_file")
    
    # Skip admin login page (has different header)
    if [[ "$filename" == "admin-login.html" ]] || [[ "$html_file" == *"/admin/"* ]]; then
        echo "⊘ Skipping admin file: $filename"
        ((skipped_count++))
        continue
    fi
    
    # Check if already has unified auth
    if has_unified_auth "$html_file"; then
        echo "✓ Already updated: $filename"
        continue
    fi
    
    echo "→ Updating: $filename"
    
    # Create temporary file
    temp_file="${html_file}.tmp"
    
    # Process the file
    awk '
    BEGIN {
        in_head = 0
        head_closed = 0
        script_added = 0
        css_added = 0
    }
    
    # Detect head tag
    /<head>/ {
        in_head = 1
        print
        next
    }
    
    # Add scripts before closing head tag
    /<\/head>/ {
        if (!css_added) {
            print "    <!-- Unified Header CSS -->"
            print "    <link rel=\"stylesheet\" href=\"/css/unified-header.css\">"
            css_added = 1
        }
        if (!script_added) {
            print "    <!-- Unified Authentication System -->"
            print "    <script src=\"/js/unified-auth.js\" defer></script>"
            script_added = 1
        }
        print
        head_closed = 1
        next
    }
    
    # If we have already added scripts in head, just print other lines
    {
        print
    }
    ' "$html_file" > "$temp_file"
    
    # Replace original file
    mv "$temp_file" "$html_file"
    
    ((updated_count++))
done

echo ""
echo "=========================================="
echo "Update Complete!"
echo "=========================================="
echo "Total files found: $total_files"
echo "Files updated: $updated_count"
echo "Files skipped: $skipped_count"
echo "Backup location: $BACKUP_DIR"
echo ""
echo "Next steps:"
echo "1. Test the homepage: http://your-domain/homepage.html"
echo "2. Test login/logout flow"
echo "3. Check responsive design on mobile"
echo "4. If issues occur, restore from backup"
echo ""
echo "To restore from backup:"
echo "  cp -r $BACKUP_DIR/* $FRONTEND_DIR/"
echo ""

