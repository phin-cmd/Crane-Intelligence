#!/bin/bash

# Setup Verification Script
# Verifies that all setup steps have been completed

echo "========================================="
echo "Setup Verification"
echo "========================================="
echo ""

ERRORS=0

# Check npm dependencies
echo "1. Checking npm dependencies..."
if [ -d "node_modules/@playwright" ]; then
    echo "   ✅ Playwright installed"
else
    echo "   ❌ Playwright not installed. Run: npm install"
    ERRORS=$((ERRORS + 1))
fi

# Check .env.test
echo "2. Checking test environment configuration..."
if [ -f ".env.test" ]; then
    echo "   ✅ .env.test exists"
    if grep -q "BASE_URL" .env.test; then
        echo "   ✅ BASE_URL configured"
    else
        echo "   ⚠️  BASE_URL not found in .env.test"
    fi
else
    echo "   ❌ .env.test missing. Create it with test configuration."
    ERRORS=$((ERRORS + 1))
fi

# Check test files
echo "3. Checking test files..."
TEST_COUNT=$(find tests -name "*.spec.ts" 2>/dev/null | wc -l)
if [ "$TEST_COUNT" -gt 0 ]; then
    echo "   ✅ Found $TEST_COUNT test file(s)"
else
    echo "   ⚠️  No test files found"
fi

# Check backup script
echo "4. Checking backup scripts..."
if [ -f "scripts/database/backup-databases.sh" ] && [ -x "scripts/database/backup-databases.sh" ]; then
    echo "   ✅ Backup script exists and is executable"
else
    echo "   ❌ Backup script missing or not executable"
    ERRORS=$((ERRORS + 1))
fi

# Check monitoring script
echo "5. Checking monitoring scripts..."
if [ -f "scripts/monitoring/health-check.sh" ] && [ -x "scripts/monitoring/health-check.sh" ]; then
    echo "   ✅ Health check script exists and is executable"
else
    echo "   ❌ Health check script missing or not executable"
    ERRORS=$((ERRORS + 1))
fi

# Check migration manager
echo "6. Checking migration manager..."
if [ -f "backend/migrations/migration_manager.py" ]; then
    echo "   ✅ Migration manager exists"
    if [ -x "backend/migrations/migration_manager.py" ]; then
        echo "   ✅ Migration manager is executable"
    else
        echo "   ⚠️  Migration manager not executable. Run: chmod +x backend/migrations/migration_manager.py"
    fi
else
    echo "   ❌ Migration manager missing"
    ERRORS=$((ERRORS + 1))
fi

# Check cron jobs
echo "7. Checking cron jobs..."
BACKUP_CRON=$(crontab -l 2>/dev/null | grep -c "backup-databases.sh" || echo "0")
HEALTH_CRON=$(crontab -l 2>/dev/null | grep -c "health-check.sh" || echo "0")

if [ "$BACKUP_CRON" -gt 0 ]; then
    echo "   ✅ Backup cron job configured ($BACKUP_CRON job(s))"
else
    echo "   ⚠️  Backup cron job not configured. Run: ./scripts/database/schedule-backups.sh"
fi

if [ "$HEALTH_CRON" -gt 0 ]; then
    echo "   ✅ Health check cron job configured ($HEALTH_CRON job(s))"
else
    echo "   ⚠️  Health check cron job not configured. Run: ./scripts/monitoring/setup-monitoring.sh"
fi

echo ""
echo "========================================="
if [ "$ERRORS" -eq 0 ]; then
    echo "✅ Setup verification complete!"
    echo "   All critical components are in place."
else
    echo "⚠️  Setup verification found $ERRORS issue(s)"
    echo "   Please address the issues above."
fi
echo "========================================="

exit $ERRORS

