#!/bin/bash

# Verify and fix script permissions

cd /root/crane || exit 1

echo "=========================================="
echo "Verifying Security Scripts"
echo "=========================================="
echo ""

# List of required scripts
SCRIPTS=(
    "test_security.sh"
    "monitor_security.sh"
    "restart-backend-secure.sh"
    "verify_security_setup.sh"
    "quick-restart.sh"
)

MISSING=0
FIXED=0

for script in "${SCRIPTS[@]}"; do
    if [ -f "$script" ]; then
        # Check if executable
        if [ ! -x "$script" ]; then
            chmod +x "$script"
            echo "✅ Fixed permissions: $script"
            ((FIXED++))
        else
            echo "✅ $script (executable)"
        fi
    else
        echo "❌ Missing: $script"
        ((MISSING++))
    fi
done

echo ""
echo "=========================================="
echo "Summary"
echo "=========================================="
echo "Found: $((${#SCRIPTS[@]} - MISSING))/${#SCRIPTS[@]} scripts"
echo "Fixed permissions: $FIXED"
echo "Missing: $MISSING"

if [ $MISSING -gt 0 ]; then
    echo ""
    echo "⚠️  Some scripts are missing. They may need to be created."
    exit 1
else
    echo ""
    echo "✅ All scripts verified!"
    exit 0
fi

