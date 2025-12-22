#!/bin/bash
set -e

echo "========================================="
echo "Setting up Git Branching Strategy"
echo "========================================="

cd /root/crane

# Ensure we're on main and up to date
git checkout main
git pull origin main

# Create develop branch if it doesn't exist
if ! git show-ref --verify --quiet refs/heads/develop; then
    echo "Creating develop branch..."
    git checkout -b develop
    git push -u origin develop
    echo "✓ develop branch created and pushed"
else
    echo "develop branch already exists"
    git checkout develop
    git pull origin develop
fi

# Create uat branch if it doesn't exist
if ! git show-ref --verify --quiet refs/heads/uat; then
    echo "Creating uat branch..."
    git checkout -b uat
    git push -u origin uat
    echo "✓ uat branch created and pushed"
else
    echo "uat branch already exists"
    git checkout uat
    git pull origin uat
fi

# Return to main
git checkout main

echo ""
echo "========================================="
echo "Branch setup complete!"
echo "========================================="
echo ""
echo "Branches:"
git branch -a
echo ""
echo "Next steps:"
echo "1. Go to GitHub repository settings"
echo "2. Set up branch protection rules (see BRANCH_PROTECTION.md)"
echo "3. Configure GitHub Actions secrets (see CI_CD_SETUP.md)"
echo ""

