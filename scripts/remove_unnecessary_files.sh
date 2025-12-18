#!/bin/bash
# Remove all unnecessary files unrelated to website functionality

set -e

cd /root/crane

echo "🧹 Removing unnecessary files..."
echo "=========================================="

# Remove optimization/audit files
echo ""
echo "1. Removing optimization/audit files..."
rm -f OPTIMIZATION_CHANGELOG.md
rm -f OPTIMIZATION_SUMMARY.md
rm -f OPTIMIZATION_PLAN.md
rm -f audit_report.json
echo "   ✅ Removed optimization files"

# Remove implementation guides
echo ""
echo "2. Removing implementation guides..."
rm -f HEADER_IMPLEMENTATION_GUIDE.md
rm -f COMPONENT_SYSTEM.md
rm -f ADMIN_RBAC_IMPLEMENTATION.md
rm -f SUBSCRIPTION_AND_REPORT_TYPE_LOGIC.md
echo "   ✅ Removed implementation guides"

# Remove verification/checklist docs
echo ""
echo "3. Removing verification/checklist docs..."
rm -f VERIFICATION_CHECKLIST.md
rm -f PRODUCTION_VERIFICATION.md
rm -f PRODUCTION_VERIFICATION_GUIDE.md
rm -f DEPLOYMENT_CHECKLIST.md
rm -f FMV_E2E_TEST_PLAN.md
echo "   ✅ Removed verification docs"

# Remove database consolidation docs
echo ""
echo "4. Removing database consolidation docs..."
rm -f DATABASE_CONSOLIDATION.md
rm -f DATABASE_CONSOLIDATION_FINAL.md
echo "   ✅ Removed database docs"

# Remove setup/configuration guides
echo ""
echo "5. Removing setup/configuration guides..."
rm -f SETUP_INSTRUCTIONS.md
rm -f SERVICE_CONFIGURATION.md
rm -f QUICK_REFERENCE.md
rm -f ADMIN_LOGIN_CREDENTIALS.md
rm -f ADMINER_CONNECTION_GUIDE.html
echo "   ✅ Removed setup guides"

# Remove changelog (not needed for website)
echo ""
echo "6. Removing changelog..."
rm -f CHANGELOG.md
echo "   ✅ Removed changelog"

# Remove test/verification scripts
echo ""
echo "7. Removing test/verification scripts..."
rm -f check_fmv_reports.py
rm -f verify-backend-routes.py
echo "   ✅ Removed test scripts"

# Remove temporary fix scripts
echo ""
echo "8. Removing temporary fix scripts..."
rm -f fix_payment_docker.sh
rm -f fix_payment_sql.sql
echo "   ✅ Removed fix scripts"

# Remove start scripts (if not essential - keeping start.sh and start-backend.sh as they might be used)
# Actually, let me check if these are used in deployment
echo ""
echo "9. Checking start scripts..."
# Keep start.sh and start-backend.sh as they might be used in deployment
echo "   ℹ️  Keeping start.sh and start-backend.sh (may be used in deployment)"

# Remove backend documentation (keep only if essential)
echo ""
echo "10. Removing backend documentation..."
rm -f backend/SECURITY.md
rm -f backend/DIGITALOCEAN_SPACES_SETUP.md
echo "   ✅ Removed backend docs"

# Remove scripts directory files that are not essential
echo ""
echo "11. Cleaning scripts directory..."
# Keep only essential scripts
cd scripts
# Remove audit/analysis scripts
rm -f project_audit.py
rm -f project_audit_comprehensive.py
rm -f analyze_databases.py
rm -f test_database_consolidation.py
# Keep consolidation and utility scripts as they might be needed
cd ..
echo "   ✅ Cleaned scripts directory"

# Remove index.js if it's not used (check if it's referenced)
echo ""
echo "12. Checking root-level files..."
# index.js might be used, so keep it
# cache-buster.js might be used, so keep it
echo "   ℹ️  Keeping index.js and cache-buster.js (may be used)"

echo ""
echo "=========================================="
echo "✅ Cleanup completed!"
echo ""
echo "Files kept for website functionality:"
echo "  ✅ All HTML files"
echo "  ✅ All JavaScript files (js/)"
echo "  ✅ All CSS files (css/)"
echo "  ✅ All backend code (backend/app/)"
echo "  ✅ All components (components/)"
echo "  ✅ All images (images/)"
echo "  ✅ All data files (data/)"
echo "  ✅ Configuration files (.gitignore, docker-compose.yml, Dockerfile, nginx.conf)"
echo "  ✅ Requirements (requirements.txt)"
echo "  ✅ Essential docs (README.md, DEPLOYMENT.md)"
echo "  ✅ Start scripts (start.sh, start-backend.sh)"
echo ""

