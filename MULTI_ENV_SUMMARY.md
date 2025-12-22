# Multi-Environment Setup Summary

## ✅ Completed Setup

Your Crane Intelligence platform now has three fully isolated environments:

### Environments

1. **Development** (`dev.craneintelligence.tech`)
   - Branch: `develop`
   - Ports: Frontend 3101, Backend 8104, DB 5534, Redis 6480
   - Database: `crane_intelligence_dev`
   - Auto-deploys on push to `develop` branch

2. **UAT/Staging** (`uat.craneintelligence.tech`)
   - Branch: `uat`
   - Ports: Frontend 3201, Backend 8204, DB 5634, Redis 6580
   - Database: `crane_intelligence_uat`
   - Auto-deploys on push to `uat` branch (with approval)

3. **Production** (`craneintelligence.tech`)
   - Branch: `main`
   - Ports: Frontend 3001, Backend 8004, DB 5434, Redis 6380
   - Database: `crane_intelligence`
   - Auto-deploys on push to `main` branch (with approval)

## File Structure

```
/root/crane/
├── docker-compose.yml              # Production
├── docker-compose.dev.yml          # Development
├── docker-compose.uat.yml          # UAT
├── config/
│   ├── dev.env.template            # Dev config template
│   ├── uat.env.template            # UAT config template
│   ├── prod.env.template           # Prod config template
│   ├── dev.env                     # Dev actual config (not in git)
│   ├── uat.env                     # UAT actual config (not in git)
│   └── prod.env                    # Prod actual config (not in git)
├── .github/workflows/
│   ├── dev-deploy.yml              # Dev CI/CD
│   ├── uat-deploy.yml              # UAT CI/CD
│   └── prod-deploy.yml             # Prod CI/CD
├── setup-git-branches.sh           # Initialize git branches
├── init-environments.sh            # Initialize databases
├── backup-databases.sh             # Backup all databases
├── restore-database.sh             # Restore from backup
└── setup-ssl-subdomains.sh        # Get SSL certs for subdomains
```

## Quick Start Commands

### Start Environments

```bash
# Development
cd /root/crane
docker compose -f docker-compose.dev.yml -p crane-dev up -d

# UAT
docker compose -f docker-compose.uat.yml -p crane-uat up -d

# Production (existing)
docker compose up -d
```

### Check Status

```bash
# Dev
docker compose -f docker-compose.dev.yml -p crane-dev ps

# UAT
docker compose -f docker-compose.uat.yml -p crane-uat ps

# Prod
docker compose ps
```

### View Logs

```bash
# Dev
docker compose -f docker-compose.dev.yml -p crane-dev logs -f

# UAT
docker compose -f docker-compose.uat.yml -p crane-uat logs -f

# Prod
docker compose logs -f
```

## Next Steps

### 1. Configure DNS

Add A records for subdomains:
- `dev.craneintelligence.tech` → Your server IP
- `uat.craneintelligence.tech` → Your server IP

See `DNS_SETUP.md` for details.

### 2. Set Up SSL Certificates

Once DNS is configured:
```bash
/root/crane/setup-ssl-subdomains.sh
```

### 3. Initialize Git Branches

```bash
/root/crane/setup-git-branches.sh
```

### 4. Configure GitHub

1. Set up branch protection rules (see `BRANCH_PROTECTION.md`)
2. Add GitHub Actions secrets (see `CI_CD_SETUP.md`)
3. Configure GitHub Environments for approvals

### 5. Fill in Environment Variables

Edit these files with real API keys:
- `config/dev.env`
- `config/uat.env`
- `config/prod.env`

**Important**: These files are NOT committed to git (they're in `.gitignore`).

### 6. Set Up Backups

Add to crontab:
```bash
crontab -e
# Add: 0 2 * * * /root/crane/backup-databases.sh >> /var/log/crane-backups.log 2>&1
```

### 7. Set Up Monitoring

- Configure Sentry for error tracking
- Set up uptime monitoring (UptimeRobot, etc.)
- Configure log aggregation

See `MONITORING_SETUP.md` for details.

## Release Process

1. **Develop**: Work on `develop` branch → auto-deploys to dev
2. **UAT**: Merge `develop` → `uat` → auto-deploys to UAT (with approval)
3. **Production**: Merge `uat` → `main` → auto-deploys to prod (with approval)

See `RELEASE_PROCESS.md` for detailed workflow.

## Important Notes

- **Never point dev/UAT at production database**
- **Always test migrations in UAT before production**
- **Use separate API keys for each environment**
- **Backup production database before any major changes**
- **Monitor production closely after deployments**

## Troubleshooting

### Containers won't start
- Check logs: `docker compose -f docker-compose.dev.yml -p crane-dev logs`
- Verify environment files exist: `ls -la config/*.env`
- Check port conflicts: `netstat -tulpn | grep <port>`

### Database connection errors
- Verify database is running: `docker compose -f docker-compose.dev.yml -p crane-dev ps db`
- Check DATABASE_URL in env file matches compose file
- Test connection: `docker compose -f docker-compose.dev.yml -p crane-dev exec db psql -U crane_dev_user -d crane_intelligence_dev`

### Nginx routing issues
- Test locally: `curl http://localhost:3101`
- Check Nginx config: `nginx -t`
- View Nginx logs: `tail -f /var/log/nginx/error.log`

## Support

For issues or questions:
1. Check relevant documentation files
2. Review logs for error messages
3. Verify environment configuration
4. Test in dev environment first

