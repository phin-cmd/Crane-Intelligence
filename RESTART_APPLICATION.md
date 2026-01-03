# How to Restart the Application

## Current Setup

Your application is running via **Docker Compose**, not as a systemd service.

---

## ✅ Correct Way to Restart

### Option 1: Using Docker Compose (Recommended)

```bash
cd /root/crane

# Restart all services
docker-compose restart

# Or restart just the backend
docker-compose restart backend

# Or restart with rebuild (if code changed)
docker-compose up -d --build backend
```

### Option 2: Using the Start Script

```bash
cd /root/crane
./start-backend.sh
```

### Option 3: Full Restart (Stop and Start)

```bash
cd /root/crane

# Stop all services
docker-compose down

# Start all services
docker-compose up -d

# Check status
docker-compose ps
```

---

## ❌ What NOT to Do

**Don't use:**
```bash
sudo systemctl restart crane-backend  # ❌ Service doesn't exist
```

The application runs in Docker containers, not as a systemd service.

---

## Troubleshooting Docker Issues

### If you see "Not supported URL scheme http+docker":

1. **Check Docker is running:**
   ```bash
   sudo systemctl status docker
   ```

2. **Start Docker if not running:**
   ```bash
   sudo systemctl start docker
   ```

3. **Check Docker socket:**
   ```bash
   ls -la /var/run/docker.sock
   ```

4. **Fix permissions if needed:**
   ```bash
   sudo chmod 666 /var/run/docker.sock
   # Or add your user to docker group:
   sudo usermod -aG docker $USER
   ```

### If containers won't start:

1. **Check logs:**
   ```bash
   docker-compose logs backend
   ```

2. **Rebuild containers:**
   ```bash
   docker-compose build --no-cache
   docker-compose up -d
   ```

3. **Check port conflicts:**
   ```bash
   netstat -tuln | grep 8004
   ```

---

## Verify Application is Running

After restarting, verify:

```bash
# Check container status
docker-compose ps

# Check backend health
curl http://localhost:8004/api/v1/health

# Check logs
docker-compose logs --tail=50 backend
```

---

## Quick Restart Command

For a quick restart with security measures:

```bash
cd /root/crane && \
docker-compose restart backend && \
sleep 5 && \
curl -s http://localhost:8004/api/v1/health && \
echo "✅ Backend restarted successfully"
```

---

## Environment Variable Application

After setting `ENVIRONMENT=production` in `config/prod.env`:

1. **Restart the backend container:**
   ```bash
   docker-compose restart backend
   ```

2. **Verify it's applied:**
   ```bash
   # Check API docs are disabled
   curl http://localhost:8004/docs
   # Should return 404
   ```

---

## Monitoring After Restart

```bash
# Watch logs
docker-compose logs -f backend

# Check security
./test_security.sh http://localhost:8004

# Monitor security events
./monitor_security.sh watch
```

