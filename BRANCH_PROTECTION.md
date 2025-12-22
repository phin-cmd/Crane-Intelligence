# GitHub Branch Protection Rules

## Required Settings

Configure these branch protection rules in your GitHub repository settings:

### For `main` branch (Production)

1. Go to: Settings → Branches → Add rule
2. Branch name pattern: `main`
3. Enable:
   - ✅ Require a pull request before merging
     - Require approvals: **2**
     - Dismiss stale pull request approvals when new commits are pushed
   - ✅ Require status checks to pass before merging
     - Require branches to be up to date before merging
     - Status checks: `Deploy to Production` (from GitHub Actions)
   - ✅ Require conversation resolution before merging
   - ✅ Include administrators
   - ✅ Restrict who can push to matching branches: (leave empty or restrict to specific users)
   - ✅ Do not allow bypassing the above settings

### For `uat` branch (UAT/Staging)

1. Go to: Settings → Branches → Add rule
2. Branch name pattern: `uat`
3. Enable:
   - ✅ Require a pull request before merging
     - Require approvals: **1**
   - ✅ Require status checks to pass before merging
     - Status checks: `Deploy to UAT Environment`
   - ✅ Include administrators
   - ✅ Do not allow bypassing the above settings

### For `develop` branch (Development)

1. Go to: Settings → Branches → Add rule
2. Branch name pattern: `develop`
3. Enable:
   - ✅ Require a pull request before merging
     - Require approvals: **1** (optional, can be 0 for faster iteration)
   - ✅ Include administrators
   - ⚠️ Do NOT restrict pushes (developers should be able to push directly)

## How to Configure

1. Navigate to your GitHub repository: `https://github.com/phin-cmd/Crane-Intelligence`
2. Click **Settings** → **Branches**
3. Click **Add rule** for each branch pattern above
4. Configure the settings as specified
5. Click **Create** to save

## Benefits

- **Prevents accidental direct pushes** to production
- **Requires code review** before merging to critical branches
- **Ensures CI/CD passes** before deployment
- **Maintains code quality** through mandatory reviews

