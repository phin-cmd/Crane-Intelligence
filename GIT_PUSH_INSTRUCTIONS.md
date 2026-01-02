# Git Push Instructions - Excluding Secrets

## Quick Push (Automated)

Run the safe push script:

```bash
cd /root/crane
bash scripts/git-push-safe.sh
```

## Manual Steps

If you prefer to do it manually:

### Step 1: Update .gitignore

The `.gitignore` file has been updated to exclude:
- `config/dev.env`
- `config/uat.env`
- `config/prod.env`
- `backups/`
- `__pycache__/`
- `*.db` files

### Step 2: Remove Secrets from Git (if already tracked)

```bash
cd /root/crane

# Remove env files from git tracking (keeps local files)
git rm --cached config/dev.env config/uat.env config/prod.env 2>/dev/null || true

# Remove backups directory
git rm --cached -r backups/ 2>/dev/null || true

# Remove Python cache
git rm --cached -r backend/__pycache__/ 2>/dev/null || true
```

### Step 3: Stage All Files

```bash
git add -A
```

### Step 4: Verify No Secrets Are Staged

```bash
# This should return nothing
git diff --cached --name-only | grep -E "config/(dev|uat|prod)\.env$|backups/"
```

If it returns files, remove them:
```bash
git reset HEAD config/dev.env config/uat.env config/prod.env
git reset HEAD backups/
```

### Step 5: Commit

```bash
git commit -m "Deploy: Payment flow, webhooks, deployment scripts, and documentation

- Configured Stripe payment integration for all environments
- Added webhook setup guides and configuration scripts
- Created payment flow testing and verification scripts
- Added deployment and database sync scripts (prod to uat/dev)
- Updated docker-compose configurations
- Added comprehensive documentation
- Updated .gitignore to exclude secrets and sensitive files"
```

### Step 6: Push to GitHub

```bash
git push origin main
```

## What Gets Pushed

✅ **Included:**
- All code changes
- Documentation files
- Configuration templates (`.env.template` files)
- Scripts and utilities
- Docker compose files
- Updated .gitignore

❌ **Excluded (Secrets):**
- `config/dev.env` (contains Stripe keys, webhook secrets)
- `config/uat.env` (contains Stripe keys, webhook secrets)
- `config/prod.env` (contains Stripe keys, webhook secrets)
- `backups/` directory
- Python cache files (`__pycache__/`)
- Database files (`*.db`)

## Verification

After pushing, verify on GitHub that:
1. ✅ No `.env` files are visible (except `.env.template`)
2. ✅ No `backups/` directory
3. ✅ All documentation files are present
4. ✅ All scripts are present

## Troubleshooting

### "Permission denied" when pushing

Check your GitHub credentials:
```bash
git config --global user.name
git config --global user.email
```

### "Secrets found in staging"

Run:
```bash
git reset HEAD config/dev.env config/uat.env config/prod.env
git reset HEAD backups/
```

### "Remote repository not found"

Check remote:
```bash
git remote -v
```

Should show:
```
origin	https://github.com/phin-cmd/Crane-Intelligence.git (fetch)
origin	https://github.com/phin-cmd/Crane-Intelligence.git (push)
```

