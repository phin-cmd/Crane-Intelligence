# Fix: Backend Not Accessible (HTTP 000 Errors)

## Problem

Security tests are failing with HTTP code `000`, which means the backend is not accessible:
```
✗ FAILED: Payment manipulation not blocked (got 000)
✗ FAILED: SQL injection not blocked (got 000)
```

## Diagnosis

The backend process is running, but not accessible. This could mean:
1. Backend is running but not listening on the expected interface
2. Firewall is blocking connections
3. Backend is running in a container but port is not exposed
4. Backend crashed but process is still running

## Solutions

### Solution 1: Check Backend Status

```bash
cd /root/crane
./check-backend.sh
```

This will:
- Check all common ports (8003, 8004, 8000, 8080)
- Check Docker containers
- Check running processes
- Provide instructions to start backend

### Solution 2: Start Backend

```bash
cd /root/crane
./start-backend-for-tests.sh
```

This will:
- Try to start backend with Docker Compose
- Fall back to direct Python execution
- Verify backend is accessible

### Solution 3: Manual Start

#### Option A: Docker Compose
```bash
cd /root/crane
docker compose up -d backend
# Wait a few seconds
curl http://localhost:8004/api/v1/health
```

#### Option B: Direct Python
```bash
cd /root/crane/backend
source venv/bin/activate  # if using venv
uvicorn app.main:app --host 0.0.0.0 --port 8003
```

#### Option C: Use Restart Script
```bash
cd /root/crane
./restart-backend-secure.sh
```

### Solution 4: Fix Process Issues

If process is running but not accessible:

```bash
# Kill existing processes
pkill -f "uvicorn.*main:app"

# Restart
cd /root/crane/backend
uvicorn app.main:app --host 0.0.0.0 --port 8003
```

### Solution 5: Check Firewall

```bash
# Check if firewall is blocking
sudo ufw status

# If needed, allow port
sudo ufw allow 8003/tcp
sudo ufw allow 8004/tcp
```

## Updated Test Script

The test script now:
- Automatically detects the correct port
- Provides helpful error messages
- Suggests how to start the backend

## Quick Fix Command

```bash
cd /root/crane && \
./check-backend.sh && \
./start-backend-for-tests.sh && \
sleep 3 && \
./test_security.sh http://localhost:8003
```

## Verify Backend is Running

After starting, verify:

```bash
# Check health endpoint
curl http://localhost:8003/api/v1/health
# OR
curl http://localhost:8004/api/v1/health

# Should return JSON with status
```

## Common Issues

### Issue: "Connection refused"
**Cause**: Backend not running or wrong port
**Fix**: Start backend with one of the methods above

### Issue: "Process running but not accessible"
**Cause**: Process crashed or listening on wrong interface
**Fix**: Kill and restart the process

### Issue: "Docker container not accessible"
**Cause**: Port not exposed or container not running
**Fix**: Check `docker compose ps` and restart if needed

## Next Steps

1. Run `./check-backend.sh` to diagnose
2. Run `./start-backend-for-tests.sh` to start
3. Run `./test_security.sh http://localhost:8003` to test


