#!/bin/bash
# Safe Git Push Script - Excludes secrets and sensitive information

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CRANE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$CRANE_DIR"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "=========================================="
echo "Safe Git Push - Excluding Secrets"
echo "=========================================="
echo ""

# Step 1: Update .gitignore
echo -e "${BLUE}Step 1: Ensuring .gitignore excludes secrets${NC}"
if ! grep -q "config/dev.env" .gitignore 2>/dev/null; then
    echo "Updating .gitignore..."
    cat >> .gitignore << 'EOF'

# Environment files with secrets
config/dev.env
config/uat.env
config/prod.env
# Keep template files
!config/*.env.template

# Backups
backups/

# Python cache
__pycache__/
*.py[cod]

# Database files
*.db
*.sqlite

# Git rewrite
.git-rewrite/
EOF
    echo -e "${GREEN}✓ .gitignore updated${NC}"
else
    echo -e "${GREEN}✓ .gitignore already configured${NC}"
fi
echo ""

# Step 2: Remove secrets from staging if they exist
echo -e "${BLUE}Step 2: Removing secrets from staging${NC}"
git rm --cached config/dev.env config/uat.env config/prod.env 2>/dev/null || true
git rm --cached -r backups/ 2>/dev/null || true
git rm --cached -r backend/__pycache__/ 2>/dev/null || true
echo -e "${GREEN}✓ Secrets removed from staging${NC}"
echo ""

# Step 3: Add all files except ignored ones
echo -e "${BLUE}Step 3: Staging files (excluding secrets)${NC}"
git add -A
echo -e "${GREEN}✓ Files staged${NC}"
echo ""

# Step 4: Verify no secrets are staged
echo -e "${BLUE}Step 4: Verifying no secrets in staging${NC}"
SECRETS_IN_STAGING=$(git diff --cached --name-only | grep -E "config/(dev|uat|prod)\.env$|backups/" || true)
if [ -n "$SECRETS_IN_STAGING" ]; then
    echo -e "${RED}✗ WARNING: Secrets found in staging!${NC}"
    echo "$SECRETS_IN_STAGING"
    echo ""
    echo "Removing from staging..."
    echo "$SECRETS_IN_STAGING" | xargs -r git rm --cached 2>/dev/null || true
fi
echo -e "${GREEN}✓ No secrets in staging${NC}"
echo ""

# Step 5: Show what will be committed
echo -e "${BLUE}Step 5: Files to be committed${NC}"
STAGED_COUNT=$(git diff --cached --name-only | wc -l)
echo "  ${STAGED_COUNT} files staged for commit"
echo ""
echo "Sample of files to commit:"
git diff --cached --name-only | head -20 | sed 's/^/  /'
if [ "$STAGED_COUNT" -gt 20 ]; then
    echo "  ... and $((STAGED_COUNT - 20)) more files"
fi
echo ""

# Step 6: Commit
echo -e "${BLUE}Step 6: Committing changes${NC}"
read -p "Enter commit message (or press Enter for default): " COMMIT_MSG
if [ -z "$COMMIT_MSG" ]; then
    COMMIT_MSG="Deploy: Payment flow, webhooks, deployment scripts, and documentation

- Configured Stripe payment integration for all environments
- Added webhook setup guides and configuration scripts
- Created payment flow testing and verification scripts
- Added deployment and database sync scripts (prod to uat/dev)
- Updated docker-compose configurations
- Added comprehensive documentation
- Updated .gitignore to exclude secrets and sensitive files"
fi

git commit -m "$COMMIT_MSG"
echo -e "${GREEN}✓ Changes committed${NC}"
echo ""

# Step 7: Push
echo -e "${BLUE}Step 7: Pushing to origin/main${NC}"
read -p "Push to GitHub? (yes/no): " -r
echo
if [[ $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    git push origin main
    echo -e "${GREEN}✓ Pushed to origin/main${NC}"
else
    echo -e "${YELLOW}⚠ Push cancelled${NC}"
    echo "You can push later with: git push origin main"
fi
echo ""

echo "=========================================="
echo -e "${GREEN}Complete!${NC}"
echo "=========================================="
echo ""
echo "Summary:"
echo "  ✓ .gitignore updated to exclude secrets"
echo "  ✓ Secrets removed from staging"
echo "  ✓ Files committed"
if [[ $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo "  ✓ Pushed to origin/main"
else
    echo "  ⏳ Ready to push (run: git push origin main)"
fi
echo ""

