# Release Process Documentation

## Overview

This document outlines the release process for promoting code changes from Development → UAT → Production environments.

## Branch Strategy

- **`main`** (or `master`): Production branch - only tested, approved code
- **`uat`**: UAT/Staging branch - pre-production testing
- **`develop`**: Development branch - active development work
- **`feature/*`**: Feature branches - individual features/fixes

## Release Flow

```
feature/* → develop → uat → main
```

### 1. Development Phase

1. Create feature branch from `develop`:
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/your-feature-name
   ```

2. Make changes and commit:
   ```bash
   git add .
   git commit -m "feat: description of changes"
   ```

3. Push feature branch and create Pull Request to `develop`

4. After review and approval, merge PR to `develop`

5. **Automatic deployment**: GitHub Actions will deploy to `dev.craneintelligence.tech` when code is pushed to `develop`

### 2. UAT Phase

1. When `develop` is stable and ready for testing:
   ```bash
   git checkout uat
   git pull origin uat
   git merge develop
   git push origin uat
   ```

2. **Automatic deployment**: GitHub Actions will deploy to `uat.craneintelligence.tech` when code is pushed to `uat`

3. Perform QA/testing on `https://uat.craneintelligence.tech/`

4. Fix any issues found in UAT:
   - Make fixes in `develop` branch
   - Merge fixes to `uat` branch
   - Re-test on UAT

### 3. Production Release

1. When UAT testing is complete and approved:
   ```bash
   git checkout main
   git pull origin main
   git merge uat
   git tag -a v1.x.x -m "Release version 1.x.x"
   git push origin main
   git push origin --tags
   ```

2. **Automatic deployment**: GitHub Actions will deploy to `craneintelligence.tech` when code is pushed to `main`

3. Monitor production:
   - Check application logs
   - Monitor error tracking (Sentry, etc.)
   - Verify key functionality

4. If issues are found:
   - **Rollback**: Revert to previous tag
   - Fix issues in `develop`
   - Re-run release process

## Database Migrations

### Development
- Migrations run automatically on deploy
- Can reset database if needed

### UAT
- Migrations run automatically on deploy
- Database should mirror production structure

### Production
- **Manual approval required** for migrations
- Always backup database before running migrations
- Test migrations on UAT first

## Pre-Release Checklist

Before promoting to production:

- [ ] All tests passing in UAT
- [ ] QA sign-off received
- [ ] Database migrations tested in UAT
- [ ] Performance testing completed
- [ ] Security review completed (if applicable)
- [ ] Documentation updated
- [ ] Rollback plan prepared
- [ ] Team notified of release

## Rollback Procedure

If production issues occur:

1. **Quick rollback**:
   ```bash
   cd /root/crane
   git checkout <previous-tag>
   docker compose build --no-cache
   docker compose up -d
   ```

2. **Database rollback** (if migration caused issues):
   ```bash
   # Restore from backup
   # Contact DBA or use backup restoration script
   ```

3. **Investigate and fix**:
   - Create hotfix branch from `main`
   - Fix issue
   - Test in UAT
   - Deploy hotfix to production

## Environment URLs

- **Development**: https://dev.craneintelligence.tech/
- **UAT**: https://uat.craneintelligence.tech/
- **Production**: https://craneintelligence.tech/

## Contact

For questions or issues with the release process, contact the DevOps team.

