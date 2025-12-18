#!/bin/bash
# Add admin header and sidebar containers to pages that don't have them

for file in *.html; do
    if [ "$file" != "login.html" ] && [ -f "$file" ]; then
        # Check if file has containers
        if ! grep -q "admin-header-container" "$file"; then
            # Find </body> tag and add containers before it
            if grep -q "</body>" "$file"; then
                # Create backup
                cp "$file" "$file.bak"
                # Add containers before </body>
                sed -i '/<\/body>/i\
    <div id="admin-header-container"></div>\
\
    <div class="admin-main">\
        <div id="admin-sidebar-container"></div>\
\
        <div class="admin-content">' "$file"
                # Close containers before </body>
                sed -i '/<\/body>/i\
        </div>\
    </div>' "$file"
                echo "Added containers to $file"
            fi
        fi
    fi
done
echo "Done!"
