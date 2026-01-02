# Quick Start Guide - Test Automation & Deployment

This guide provides quick reference commands for the test automation and deployment workflow.

## 🚀 Quick Commands

### Running Tests

```bash
# Install dependencies
npm install

# Run all tests
npm test

# Run tests for specific environment
npm run test:dev      # Dev environment
npm run test:uat       # UAT environment  
npm run test:prod      # Production environment

# Run specific test types
npm run test:smoke     # Smoke tests only
npm run test:critical  # Critical path tests

# Run in UI mode (interactive)
npm run test:ui

# Run in debug mode
npm run test:debug
```

### Database Migrations

```bash
# Check migration status
python backend/migrations/migration_manager.py status --env dev

# Create new migration
python backend/migrations/migration_manager.py create --name migration_name

# Apply all pending migrations
python backend/migrations/migration_manager.py migrate --env dev

# Rollback a migration
python backend/migrations/migration_manager.py rollback --name migration_name --env dev

# Or use the script
./scripts/database/run-migrations.sh dev
```

### Database Backups

```bash
# Manual backup (all environments)
./scripts/database/backup-databases.sh

# Setup automated daily backups
./scripts/database/schedule-backups.sh

# Restore database
./scripts/database/restore-database.sh <env> <backup_file>

# Examples:
./scripts/database/restore-database.sh dev backups/dev_db_20241227_020000.sql.gz
./scripts/database/restore-database.sh production backups/prod_db_20241227_020000.sql.gz
```

### Health Monitoring

```bash
# Manual health check
./scripts/monitoring/health-check.sh dev
./scripts/monitoring/health-check.sh uat
./scripts/monitoring/health-check.sh production

# Setup automated monitoring (every 5 minutes)
./scripts/monitoring/setup-monitoring.sh

# Check health via API
curl https://dev.craneintelligence.tech/api/v1/health
curl https://dev.craneintelligence.tech/api/v1/health/detailed
curl https://dev.craneintelligence.tech/api/v1/health/metrics
```

## 📋 Deployment Workflow

### 1. Develop Feature

```bash
git checkout develop
git pull origin develop
git checkout -b feature/new-feature
# Make changes
git commit -m "feat: add new feature"
git push origin feature/new-feature
```

### 2. Test in Dev

```bash
# Tests run automatically on push to develop
# Or run manually:
npm run test:dev
```

### 3. Deploy to Dev

```bash
# Automatic via GitHub Actions on push to develop
# Or manually:
git checkout develop
git push origin develop
```

### 4. Promote to UAT

```bash
git checkout uat
git merge develop
git push origin uat
# Requires manual approval in GitHub
```

### 5. Promote to Production

```bash
git checkout main
git merge uat
git push origin main
# Requires manual approval in GitHub
```

## 🔧 Common Tasks

### Before Schema Changes

```bash
# 1. Backup database
./scripts/database/backup-databases.sh

# 2. Create migration
python backend/migrations/migration_manager.py create --name add_new_table

# 3. Write migration SQL
# Edit: backend/migrations/YYYYMMDD_HHMMSS_add_new_table.sql

# 4. Write rollback SQL
# Edit: backend/migrations/YYYYMMDD_HHMMSS_add_new_table_rollback.sql

# 5. Test in dev
python backend/migrations/migration_manager.py migrate --env dev

# 6. Verify
python backend/migrations/migration_manager.py status --env dev
```

### Emergency Rollback

```bash
# 1. Stop application
docker compose stop backend

# 2. Restore database
./scripts/database/restore-database.sh production backups/prod_db_YYYYMMDD_HHMMSS.sql.gz

# 3. Revert code
git revert <commit-hash>
git push origin main

# 4. Restart
docker compose restart backend
```

### Check System Status

```bash
# Health check
curl https://craneintelligence.tech/api/v1/health/detailed | jq

# Database status
curl https://craneintelligence.tech/api/v1/health/database | jq

# System metrics
curl https://craneintelligence.tech/api/v1/health/metrics | jq
```

## 📚 Documentation

- **Full Testing Plan**: `END_TO_END_AUTOMATION_TESTING_PLAN.md`
- **Migration Guide**: `backend/migrations/MIGRATION_GUIDE.md`
- **Backup/Restore**: `scripts/database/BACKUP_RESTORE_GUIDE.md`
- **Monitoring**: `MONITORING_GUIDE.md`
- **Implementation Summary**: `IMPLEMENTATION_SUMMARY.md`

## ⚠️ Important Reminders

1. **Always backup before migrations** (especially production)
2. **Test in dev first** before UAT/production
3. **Verify health checks** after deployment
4. **Monitor logs** for issues
5. **Use rollback** if something goes wrong

## 🆘 Troubleshooting

### Tests Failing
- Check test environment is running
- Verify database connection
- Check test user credentials

### Migration Fails
- Check error message
- Verify SQL syntax
- Check database permissions
- Restore from backup if needed

### Health Check Fails
- Check service is running
- Check database connection
- Review application logs
- Check system resources

---

For detailed information, see the respective guide documents.

