#!/bin/bash
# Script to apply admin layout to all admin pages

for file in *.html; do
    if [ "$file" != "login.html" ] && [ -f "$file" ]; then
        # Check if file already has admin-layout.js
        if ! grep -q "admin-layout.js" "$file"; then
            # Replace admin-header.js with admin-layout.js if it exists
            if grep -q "admin-header.js" "$file"; then
                sed -i 's|js/admin-header.js|js/admin-layout.js|g' "$file"
                echo "Updated $file"
            fi
        fi
    fi
done
echo "Done!"
