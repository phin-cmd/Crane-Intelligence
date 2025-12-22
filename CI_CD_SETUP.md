# CI/CD Setup Guide

## GitHub Actions Secrets Configuration

To enable automated deployments, configure these secrets in your GitHub repository:

### Required Secrets

1. Go to: Settings → Secrets and variables → Actions → New repository secret

2. Add the following secrets:

#### SSH Access
- **Name**: `SSH_KEY`
- **Value**: Your private SSH key (content of `~/.ssh/id_rsa` or similar)
- **Description**: Private SSH key for server access

#### Dev Environment
- **Name**: `DEV_HOST`
- **Value**: Your server IP or hostname (e.g., `129.212.177.131`)
- **Description**: Dev server hostname/IP

- **Name**: `DEV_USER`
- **Value**: `root` (or your SSH username)
- **Description**: SSH username for dev server

#### UAT Environment
- **Name**: `UAT_HOST`
- **Value**: Your server IP or hostname (same as dev if on same server)
- **Description**: UAT server hostname/IP

- **Name**: `UAT_USER`
- **Value**: `root` (or your SSH username)
- **Description**: SSH username for UAT server

#### Production Environment
- **Name**: `PROD_HOST`
- **Value**: Your server IP or hostname
- **Description**: Production server hostname/IP

- **Name**: `PROD_USER`
- **Value**: `root` (or your SSH username)
- **Description**: SSH username for production server

## GitHub Environments

Configure environments in GitHub for deployment approvals:

1. Go to: Settings → Environments → New environment

2. Create **`uat`** environment:
   - Name: `uat`
   - Protection rules: Optional (can require manual approval)
   - Deployment branches: `uat` branch only

3. Create **`production`** environment:
   - Name: `production`
   - Protection rules: ✅ Required reviewers (add yourself/team)
   - Deployment branches: `main` branch only
   - Wait timer: Optional (e.g., 5 minutes delay)

## Workflow Files

The following workflow files are already created:

- `.github/workflows/dev-deploy.yml` - Deploys on push to `develop`
- `.github/workflows/uat-deploy.yml` - Deploys on push to `uat` (requires UAT environment approval)
- `.github/workflows/prod-deploy.yml` - Deploys on push to `main` (requires production environment approval)

## Testing the Setup

1. **Test dev deployment**:
   ```bash
   git checkout develop
   # Make a small change
   git commit -m "test: dev deployment"
   git push origin develop
   ```
   - Check GitHub Actions tab for workflow run
   - Verify deployment to `https://dev.craneintelligence.tech/`

2. **Test UAT deployment**:
   ```bash
   git checkout uat
   git merge develop
   git push origin uat
   ```
   - Approve deployment in GitHub Environments
   - Verify deployment to `https://uat.craneintelligence.tech/`

3. **Test production deployment**:
   ```bash
   git checkout main
   git merge uat
   git push origin main
   ```
   - Approve deployment in GitHub Environments
   - Verify deployment to `https://craneintelligence.tech/`

## Troubleshooting

### SSH Connection Issues

If deployments fail with SSH errors:

1. Verify SSH key is correct and has proper permissions
2. Test SSH connection manually:
   ```bash
   ssh -i ~/.ssh/your_key root@your-server-ip
   ```
3. Ensure GitHub Actions can access the server (firewall rules)

### Deployment Failures

Check GitHub Actions logs for:
- Docker build errors
- Container startup issues
- Database connection problems
- Missing environment variables

