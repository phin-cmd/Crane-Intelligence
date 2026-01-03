# Environment Setup Guide

## Setting ENVIRONMENT=production

To enable all security measures in production, you need to set the `ENVIRONMENT` variable.

---

## Option 1: Update Existing Environment File

If you're using environment-specific files (like `config/prod.env`):

```bash
# Edit the production environment file
nano config/prod.env

# Add or update this line:
ENVIRONMENT=production
```

---

## Option 2: Create .env File in Backend

If you're using a `.env` file in the backend directory:

```bash
cd backend

# Create .env file if it doesn't exist
touch .env

# Add environment variable
echo "ENVIRONMENT=production" >> .env

# Verify it was added
grep ENVIRONMENT .env
```

---

## Option 3: Set as System Environment Variable

For Docker or systemd services:

```bash
# For Docker
export ENVIRONMENT=production

# For systemd service
# Edit the service file and add:
# Environment="ENVIRONMENT=production"
```

---

## Option 4: Update Docker Compose

If using Docker Compose, update `docker-compose.yml`:

```yaml
services:
  backend:
    environment:
      - ENVIRONMENT=production
    # ... other config
```

---

## Verification

After setting the environment variable, verify it's working:

```bash
# Check if environment is set
python3 -c "import os; print('ENVIRONMENT:', os.getenv('ENVIRONMENT', 'not set'))"

# Or check in the application
curl http://localhost:8003/api/v1/health | grep environment
```

---

## Important Notes

1. **API Documentation**: When `ENVIRONMENT=production`, API docs at `/docs` will be disabled
2. **Error Messages**: Error messages will be sanitized in production
3. **Security Features**: All security features are active in production mode

---

## Testing

After setting the environment variable:

1. Restart your application
2. Run security tests: `./test_security.sh`
3. Verify API docs are disabled: `curl http://localhost:8003/docs` (should return 404)

---

## Current Configuration

Your application will check for `ENVIRONMENT` in this order:
1. System environment variable
2. `.env` file in backend directory
3. Default: `production` (secure by default)

---

**Note**: The application defaults to `production` mode if `ENVIRONMENT` is not set, so security measures are active by default.

