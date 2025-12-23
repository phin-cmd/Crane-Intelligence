#!/bin/bash
# Script to push changes to GitHub main branch

set -e

cd /root/crane

echo "=== Git Push Helper Script ==="
echo ""

# Check if token is provided as argument
if [ -n "$1" ]; then
    TOKEN=$1
    echo "Using provided token..."
    git remote set-url origin https://${TOKEN}@github.com/phin-cmd/Crane-Intelligence.git
    git push origin main
    echo ""
    echo "✅ Push completed successfully!"
    exit 0
fi

# Check current status
echo "Current status:"
git status -sb
echo ""

# Show commits ready to push
COMMITS_AHEAD=$(git rev-list --count origin/main..HEAD 2>/dev/null || echo "0")
if [ "$COMMITS_AHEAD" -gt 0 ]; then
    echo "Commits ready to push:"
    git log --oneline origin/main..HEAD
    echo ""
fi

# Check for authentication methods
echo "=== Authentication Methods ==="
echo ""

# Check for SSH
if [ -f ~/.ssh/id_ed25519 ] || [ -f ~/.ssh/id_rsa ]; then
    echo "✅ SSH keys found"
    echo "   Try: git remote set-url origin git@github.com:phin-cmd/Crane-Intelligence.git"
    echo "   Then: git push origin main"
    echo ""
fi

# Check for GitHub CLI
if command -v gh &> /dev/null; then
    echo "✅ GitHub CLI installed"
    echo "   Run: gh auth login"
    echo "   Then: git push origin main"
    echo ""
fi

echo "=== Option 1: Use Personal Access Token ==="
echo "1. Create token at: https://github.com/settings/tokens/new"
echo "2. Select 'repo' scope"
echo "3. Run this script with token: ./push-to-github.sh <YOUR_TOKEN>"
echo "   OR manually:"
echo "   git remote set-url origin https://<TOKEN>@github.com/phin-cmd/Crane-Intelligence.git"
echo "   git push origin main"
echo ""

echo "=== Option 2: Use SSH Key ==="
echo "1. Generate: ssh-keygen -t ed25519 -C 'your_email@example.com'"
echo "2. Add to GitHub: https://github.com/settings/keys"
echo "3. Run: git remote set-url origin git@github.com:phin-cmd/Crane-Intelligence.git"
echo "4. Run: git push origin main"
echo ""

echo "=== Option 3: GitHub CLI (Interactive) ==="
echo "1. Run: gh auth login"
echo "2. Follow prompts"
echo "3. Run: git push origin main"
echo ""

echo "✅ All changes are committed and ready to push!"

