# Dev Environment Deployment Guide

## Overview
This guide covers deploying the optimized codebase to the dev environment (https://dev.craneintelligence.tech/).

## Prerequisites
- Docker and Docker Compose installed
- Access to dev environment
- Dev database credentials configured
- Environment variables set in `config/dev.env`

## Pre-Deployment Checklist

1. ✅ All changes committed to `dev-optimization` branch
2. ✅ Backups created
3. ✅ Code consolidated and optimized
4. ⏳ Dev database optimized (if needed)
5. ⏳ Tests passing
6. ⏳ Production verified as untouched

## Deployment Steps

### 1. Verify Branch
```bash
cd /root/crane
git branch
# Should show: * dev-optimization
```

### 2. Check Dev Environment Configuration
```bash
# Verify dev.env exists and is configured
cat config/dev.env

# Verify docker-compose.dev.yml
cat docker-compose.dev.yml
```

### 3. Stop Existing Dev Containers (if running)
```bash
docker compose -f docker-compose.dev.yml -p crane-dev down
```

### 4. Build and Start Dev Services
```bash
# Build images
docker compose -f docker-compose.dev.yml -p crane-dev build --no-cache

# Start services
docker compose -f docker-compose.dev.yml -p crane-dev up -d
```

### 5. Verify Services Are Running
```bash
# Check service status
docker compose -f docker-compose.dev.yml -p crane-dev ps

# Check logs
docker compose -f docker-compose.dev.yml -p crane-dev logs -f
```

### 6. Verify Dev Environment Access
- Frontend: https://dev.craneintelligence.tech/
- Backend API: https://dev.craneintelligence.tech/api
- Adminer: http://localhost:8182 (if exposed)

### 7. Run Smoke Tests
```bash
# Test API health
curl https://dev.craneintelligence.tech/api/health

# Test authentication endpoint
curl https://dev.craneintelligence.tech/api/v1/auth/health
```

## Post-Deployment Verification

### Functional Tests
1. ✅ User registration/login works
2. ✅ Valuation terminal loads
3. ✅ FMV report generation works
4. ✅ Admin portal accessible
5. ✅ Email notifications work
6. ✅ Database connections working

### Performance Checks
- API response times acceptable
- Database queries optimized
- No memory leaks
- Services stable

## Rollback Procedure

If issues are detected:

```bash
# Stop dev containers
docker compose -f docker-compose.dev.yml -p crane-dev down

# Restore from backup
# (Backup location: /root/backups/dev-pre-optimization-YYYYMMDD-HHMMSS/)

# Switch back to previous commit if needed
git checkout <previous-commit-hash>
```

## Monitoring

### Check Logs
```bash
# All services
docker compose -f docker-compose.dev.yml -p crane-dev logs -f

# Specific service
docker compose -f docker-compose.dev.yml -p crane-dev logs -f backend
docker compose -f docker-compose.dev.yml -p crane-dev logs -f frontend
```

### Check Database
```bash
# Connect to dev database
docker exec -it crane-dev-db-1 psql -U crane_dev_user -d crane_intelligence_dev
```

## Troubleshooting

### Services Won't Start
- Check Docker logs: `docker compose -f docker-compose.dev.yml -p crane-dev logs`
- Verify environment variables in `config/dev.env`
- Check port conflicts: `netstat -tulpn | grep -E ':(3101|8104|5534)'`

### Database Connection Issues
- Verify database container is running: `docker compose -f docker-compose.dev.yml -p crane-dev ps db`
- Check database credentials in `config/dev.env`
- Verify network connectivity between containers

### API Not Responding
- Check backend logs: `docker compose -f docker-compose.dev.yml -p crane-dev logs backend`
- Verify backend container is running
- Check API endpoint: `curl https://dev.craneintelligence.tech/api/health`

## Notes

- **Production is completely safe** - no changes made to production
- All changes are in `dev-optimization` branch only
- Dev database is separate from production
- All backups are available in `/root/backups/`

## Support

For issues or questions:
- Check `OPTIMIZATION_CHANGELOG.md` for changes made
- Review `docs/ARCHIVE_README.md` for historical context
- Check Git commit history: `git log --oneline`

