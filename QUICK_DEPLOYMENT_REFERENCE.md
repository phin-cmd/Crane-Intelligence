# Quick Deployment Reference

## ⚠️ CRITICAL: Always Use Environment-Specific Scripts

**Problem**: All environments share the same code directory. Deployments must be isolated to prevent affecting other environments.

**Solution**: Use the scripts below to deploy to a SINGLE environment only.

---

## Quick Commands

### Deploy to Single Environment

```bash
# DEV only
./scripts/deployment/deploy-to-dev.sh

# UAT only
./scripts/deployment/deploy-to-uat.sh

# PRODUCTION only (requires confirmation)
./scripts/deployment/deploy-to-production.sh
```

### Restart Single Environment

```bash
# Restart DEV backend only
./scripts/restart-backend-single-env.sh dev

# Restart UAT backend only
./scripts/restart-backend-single-env.sh uat

# Restart PRODUCTION backend only
./scripts/restart-backend-single-env.sh prod
```

---

## ❌ DO NOT USE (Unless Deploying to Multiple Environments)

```bash
# ❌ Restarts ALL environments
./scripts/restart-backends-with-env-config.sh

# ❌ Deploys to BOTH dev and UAT
./deploy-to-environments.sh
```

---

## Verification

After deploying, verify only target environment was affected:

```bash
# Check all containers are still running
docker ps | grep backend

# Verify environment
docker exec <container-name> env | grep ENVIRONMENT
```

---

## Environment Ports

| Environment | Backend | Frontend | Database |
|-------------|---------|----------|----------|
| DEV | 8104 | 3101 | 5534 |
| UAT | 8204 | 3201 | 5634 |
| Production | 8004 | 3001 | 5434 |

---

## Container Names

- DEV: `crane-dev-backend-1`
- UAT: `crane-uat-backend-1`
- Production: `crane-backend-1`

---

## Full Documentation

See `DEPLOYMENT_WORKFLOW.md` for complete guide.

