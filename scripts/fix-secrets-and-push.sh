#!/bin/bash
# Fix secrets in template files and push to GitHub

set -e

cd /root/crane

echo "=========================================="
echo "Fixing Secrets and Pushing to GitHub"
echo "=========================================="
echo ""

# Verify the fix was applied
if grep -q "replace-with-brevo-api-key" config/prod.env.template; then
    echo "✓ prod.env.template already fixed"
else
    echo "Fixing prod.env.template..."
    sed -i 's/BREVO_API_KEY=xkeysib-.*/BREVO_API_KEY=replace-with-brevo-api-key-from-brevo-dashboard/' config/prod.env.template
    sed -i 's/BREVO_SMTP_PASSWORD=CraneIntel123!/BREVO_SMTP_PASSWORD=replace-with-brevo-smtp-password/' config/prod.env.template
    echo "✓ prod.env.template fixed"
fi

# Stage the fix
git add config/prod.env.template

# Amend the last commit
echo ""
echo "Amending last commit..."
git commit --amend --no-edit

# Push with force-with-lease (safer than force)
echo ""
echo "Pushing to GitHub..."
git push origin main --force-with-lease

echo ""
echo "=========================================="
echo "✓ Successfully pushed to GitHub!"
echo "=========================================="

