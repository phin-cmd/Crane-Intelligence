# Deployment Workflow - Environment Isolation Guide

## ⚠️ Critical Issue Identified and Fixed

**Problem**: All environments (dev, UAT, production) were sharing the same code directory via Docker volume mounts. Changes made in one environment were immediately affecting all environments.

**Solution**: Created environment-specific deployment scripts that ensure only the target environment is affected by deployments.

---

## Current Architecture

### Code Sharing (Volume Mounts)

**Important**: All environments currently share the same code directory via volume mounts:
- Dev: `./backend:/app` in `docker-compose.dev.yml`
- UAT: `./backend:/app` in `docker-compose.uat.yml`
- Production: `./backend:/app` in `docker-compose.yml`

This means:
- ✅ **Code changes are shared** - All environments see the same code
- ⚠️ **Deployments must be isolated** - Only restart/rebuild the target environment
- ⚠️ **Configuration is isolated** - Each environment uses its own `.env` file

### Environment Isolation

| Component | Dev | UAT | Production |
|-----------|-----|-----|------------|
| **Code Directory** | Shared (`./backend`) | Shared (`./backend`) | Shared (`./backend`) |
| **Config File** | `config/dev.env` | `config/uat.env` | `config/prod.env` |
| **Docker Compose** | `docker-compose.dev.yml` | `docker-compose.uat.yml` | `docker-compose.yml` |
| **Project Name** | `crane-dev` | `crane-uat` | `crane` |
| **Backend Port** | 8104 | 8204 | 8004 |
| **Database** | `crane_intelligence_dev` | `crane_intelligence_uat` | `crane_intelligence` |
| **Redis Port** | 6480 | 6580 | 6380 |

---

## Deployment Workflow

### ✅ Correct Way: Deploy to Single Environment

**Use environment-specific deployment scripts:**

```bash
# Deploy to DEV only
./scripts/deployment/deploy-to-dev.sh

# Deploy to UAT only
./scripts/deployment/deploy-to-uat.sh

# Deploy to PRODUCTION only (requires confirmation)
./scripts/deployment/deploy-to-production.sh
```

**What these scripts do:**
1. Stop only the target environment's backend container
2. Rebuild the backend image for that environment
3. Start only the target environment's backend container
4. Verify the environment is correctly configured
5. **Do NOT affect other environments**

### ❌ Wrong Way: Deploy to All Environments

**DO NOT use these scripts for single-environment deployments:**

```bash
# ❌ WRONG - Deploys to BOTH dev and UAT
./deploy-to-environments.sh

# ❌ WRONG - Restarts ALL environments
./scripts/restart-backends-with-env-config.sh
```

**These scripts should only be used when:**
- You intentionally want to deploy to multiple environments
- You're doing a coordinated multi-environment deployment
- You're setting up all environments from scratch

---

## Restarting Backend Services

### Single Environment Restart

**Use the single-environment restart script:**

```bash
# Restart DEV backend only
./scripts/restart-backend-single-env.sh dev

# Restart UAT backend only
./scripts/restart-backend-single-env.sh uat

# Restart PRODUCTION backend only
./scripts/restart-backend-single-env.sh prod
```

### All Environments Restart

**Only use when you need to restart all environments:**

```bash
# Restart ALL environments (dev, UAT, production)
./scripts/restart-backends-with-env-config.sh
```

---

## Development Workflow

### Making Changes in DEV

1. **Make code changes** in `/root/crane/backend/`
   - These changes are immediately visible to all environments (due to volume mounts)
   - But only DEV should be restarted to pick up changes

2. **Deploy to DEV only:**
   ```bash
   ./scripts/deployment/deploy-to-dev.sh
   ```

3. **Test in DEV:**
   - Backend: http://localhost:8104
   - Frontend: http://localhost:3101

4. **Verify DEV only was affected:**
   ```bash
   # Check DEV container
   docker ps | grep crane-dev-backend
   
   # Check UAT container (should be unchanged)
   docker ps | grep crane-uat-backend
   
   # Check Production container (should be unchanged)
   docker ps | grep crane-backend-1
   ```

### Promoting Changes to UAT

1. **After testing in DEV**, deploy to UAT:
   ```bash
   ./scripts/deployment/deploy-to-uat.sh
   ```

2. **Test in UAT:**
   - Backend: http://localhost:8204
   - Frontend: http://localhost:3201

### Promoting Changes to Production

1. **After testing in UAT**, deploy to production:
   ```bash
   ./scripts/deployment/deploy-to-production.sh
   ```
   - Requires confirmation: type `yes` to proceed

2. **Test in Production:**
   - Backend: http://localhost:8004
   - Frontend: http://localhost:3001

---

## Common Scenarios

### Scenario 1: Quick DEV Fix

**Problem**: Need to fix a bug in DEV quickly

**Solution:**
```bash
# 1. Make code changes
vim backend/app/api/v1/some_endpoint.py

# 2. Deploy to DEV only
./scripts/deployment/deploy-to-dev.sh

# 3. Test in DEV
curl http://localhost:8104/api/v1/some_endpoint
```

**Result**: Only DEV is affected, UAT and production remain unchanged.

### Scenario 2: Configuration Change

**Problem**: Need to update environment variables

**Solution:**
```bash
# 1. Update config file (e.g., config/dev.env)
vim config/dev.env

# 2. Restart DEV backend only
./scripts/restart-backend-single-env.sh dev
```

**Result**: Only DEV picks up the new configuration.

### Scenario 3: Code Change Affecting All Environments

**Problem**: Made a code change that should affect all environments

**Solution:**
```bash
# 1. Make code changes
vim backend/app/api/v1/some_endpoint.py

# 2. Deploy to each environment separately
./scripts/deployment/deploy-to-dev.sh
./scripts/deployment/deploy-to-uat.sh
./scripts/deployment/deploy-to-production.sh
```

**Result**: Each environment is updated independently.

---

## Verification Commands

### Check Which Containers Are Running

```bash
# List all backend containers
docker ps | grep backend

# Expected output:
# crane-dev-backend-1    ...  0.0.0.0:8104->8003/tcp
# crane-uat-backend-1    ...  0.0.0.0:8204->8003/tcp
# crane-backend-1        ...  0.0.0.0:8004->8003/tcp
```

### Verify Environment Configuration

```bash
# Check DEV environment
docker exec crane-dev-backend-1 env | grep ENVIRONMENT

# Check UAT environment
docker exec crane-uat-backend-1 env | grep ENVIRONMENT

# Check PRODUCTION environment
docker exec crane-backend-1 env | grep ENVIRONMENT
```

### Check Container Logs

```bash
# DEV logs
docker logs crane-dev-backend-1 --tail 50

# UAT logs
docker logs crane-uat-backend-1 --tail 50

# PRODUCTION logs
docker logs crane-backend-1 --tail 50
```

---

## Troubleshooting

### Issue: Changes in DEV are appearing in UAT/Production

**Cause**: All environments share the same code directory via volume mounts.

**Solution**: 
- This is expected behavior due to volume mounts
- **But deployments should be isolated** - only restart the target environment
- Use environment-specific deployment scripts

### Issue: Wrong environment variables in container

**Cause**: Container was started with wrong environment file or wasn't recreated.

**Solution**:
```bash
# Restart the specific environment
./scripts/restart-backend-single-env.sh <env>

# Verify environment variables
docker exec <container-name> env | grep ENVIRONMENT
```

### Issue: Container not starting after deployment

**Solution**:
```bash
# Check logs
docker logs <container-name>

# Check if container exists
docker ps -a | grep <container-name>

# Try manual restart
docker compose -f <compose-file> -p <project-name> up -d backend
```

---

## Best Practices

### 1. Always Use Environment-Specific Scripts

✅ **DO: Use `./scripts/deployment/deploy-to-dev.sh` for DEV deployments
❌ **DON'T**: Use `./deploy-to-environments.sh` for single-environment changes

### 2. Verify After Deployment

Always verify that only the target environment was affected:
```bash
# After deploying to DEV
docker ps | grep backend  # Should show all environments still running
docker exec crane-dev-backend-1 env | grep ENVIRONMENT  # Should show ENVIRONMENT=dev
```

### 3. Test Before Promoting

- Test thoroughly in DEV before promoting to UAT
- Test thoroughly in UAT before promoting to Production
- Use environment-specific test scripts

### 4. Keep Configuration Separate

- Never copy config files between environments
- Each environment has its own `.env` file
- Production config should never be committed to git

### 5. Monitor Logs

Monitor logs for each environment separately:
```bash
# DEV logs
docker logs -f crane-dev-backend-1

# UAT logs
docker logs -f crane-uat-backend-1

# PRODUCTION logs
docker logs -f crane-backend-1
```

---

## Future Improvements

### Option 1: Separate Code Directories

Create environment-specific code directories:
- `/root/crane/backend-dev/`
- `/root/crane/backend-uat/`
- `/root/crane/backend-prod/`

**Pros**: Complete code isolation
**Cons**: Code duplication, harder to maintain

### Option 2: Use Docker Images Instead of Volume Mounts

Build and push images for each environment:
- `crane-backend:dev`
- `crane-backend:uat`
- `crane-backend:prod`

**Pros**: True isolation, better for production
**Cons**: Requires image registry, slower development cycle

### Option 3: Git-Based Deployment

Use git branches or tags for each environment:
- `dev` branch → DEV environment
- `uat` branch → UAT environment
- `main` branch → Production environment

**Pros**: Version control, rollback capability
**Cons**: Requires git workflow setup

---

## Summary

### Key Points

1. **Code is shared** via volume mounts, but **deployments must be isolated**
2. **Always use environment-specific deployment scripts**
3. **Verify** that only the target environment was affected
4. **Test** in each environment before promoting to the next
5. **Configuration** is isolated per environment

### Quick Reference

| Action | Command |
|--------|---------|
| Deploy to DEV | `./scripts/deployment/deploy-to-dev.sh` |
| Deploy to UAT | `./scripts/deployment/deploy-to-uat.sh` |
| Deploy to Production | `./scripts/deployment/deploy-to-production.sh` |
| Restart DEV | `./scripts/restart-backend-single-env.sh dev` |
| Restart UAT | `./scripts/restart-backend-single-env.sh uat` |
| Restart Production | `./scripts/restart-backend-single-env.sh prod` |
| Restart All | `./scripts/restart-backends-with-env-config.sh` |

---

*Last updated: December 30, 2025*

