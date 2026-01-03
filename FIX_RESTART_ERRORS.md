# Fix Restart Errors - Troubleshooting Guide

## Issues Identified

1. **Docker Compose Error**: `Not supported URL scheme http+docker`
2. **Systemd Service Error**: `Unit crane-backend.service not found`

---

## Solution 1: Fix Docker Compose Issue

### Problem
The error `Not supported URL scheme http+docker` indicates Docker daemon connection issues.

### Fix Steps

#### Step 1: Check Docker Status
```bash
sudo systemctl status docker
```

#### Step 2: Start Docker (if not running)
```bash
sudo systemctl start docker
sudo systemctl enable docker  # Enable on boot
```

#### Step 3: Check Docker Socket Permissions
```bash
ls -la /var/run/docker.sock
```

If permissions are wrong:
```bash
sudo chmod 666 /var/run/docker.sock
# OR add your user to docker group:
sudo usermod -aG docker $USER
newgrp docker  # Apply group change
```

#### Step 4: Test Docker
```bash
docker ps
```

#### Step 5: Use Correct Docker Compose Command
```bash
# Try newer syntax first
docker compose ps

# Or older syntax
docker-compose ps
```

---

## Solution 2: Application Runs in Docker, Not Systemd

### Problem
The error `Unit crane-backend.service not found` means there's no systemd service. Your app runs in Docker containers.

### Correct Restart Methods

#### Method 1: Docker Compose (Recommended)
```bash
cd /root/crane

# Restart backend only
docker compose restart backend
# OR
docker-compose restart backend

# Restart all services
docker compose restart
# OR
docker-compose restart
```

#### Method 2: Using the Restart Script
```bash
cd /root/crane
./restart-backend-secure.sh
```

#### Method 3: Full Restart
```bash
cd /root/crane

# Stop all
docker compose down
# OR
docker-compose down

# Start all
docker compose up -d
# OR
docker-compose up -d
```

---

## Solution 3: Alternative - Run Without Docker

If Docker is not available, you can run the backend directly:

### Option A: Using Python Directly
```bash
cd /root/crane/backend

# Activate virtual environment (if exists)
source venv/bin/activate  # or python3 -m venv venv && source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run with uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8003
```

### Option B: Create Systemd Service (if needed)
```bash
sudo nano /etc/systemd/system/crane-backend.service
```

Add this content:
```ini
[Unit]
Description=Crane Intelligence Backend
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/root/crane/backend
Environment="ENVIRONMENT=production"
EnvironmentFile=/root/crane/config/prod.env
ExecStart=/usr/bin/python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8003
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable crane-backend
sudo systemctl start crane-backend
sudo systemctl status crane-backend
```

---

## Quick Fix Commands

### If Docker is the issue:
```bash
# Fix Docker
sudo systemctl start docker
sudo usermod -aG docker $USER
newgrp docker

# Then restart
cd /root/crane
docker compose restart backend
```

### If you want to use the restart script:
```bash
cd /root/crane
chmod +x restart-backend-secure.sh
./restart-backend-secure.sh
```

### If Docker is not available:
```bash
cd /root/crane/backend
source venv/bin/activate 2>/dev/null || python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
ENVIRONMENT=production uvicorn app.main:app --host 0.0.0.0 --port 8003
```

---

## Verify After Restart

```bash
# Check if backend is running
curl http://localhost:8004/api/v1/health
# OR if running directly:
curl http://localhost:8003/api/v1/health

# Check API docs are disabled (should be 404)
curl http://localhost:8004/docs
# OR
curl http://localhost:8003/docs

# Check security headers
curl -I http://localhost:8004 | grep -i "x-frame"
```

---

## Common Issues and Solutions

### Issue: "Cannot connect to Docker daemon"
**Solution:**
```bash
sudo systemctl start docker
sudo usermod -aG docker $USER
```

### Issue: "docker-compose: command not found"
**Solution:**
```bash
# Install docker-compose
sudo apt-get update
sudo apt-get install docker-compose
# OR use newer syntax:
docker compose version
```

### Issue: "Port already in use"
**Solution:**
```bash
# Find what's using the port
sudo lsof -i :8004
# OR
sudo netstat -tuln | grep 8004

# Kill the process or change port in docker-compose.yml
```

### Issue: "Container keeps restarting"
**Solution:**
```bash
# Check logs
docker compose logs backend
# OR
docker-compose logs backend

# Check for errors in the logs
```

---

## Recommended Approach

1. **First, try Docker Compose:**
   ```bash
   cd /root/crane
   docker compose restart backend
   ```

2. **If that fails, check Docker:**
   ```bash
   sudo systemctl status docker
   ```

3. **If Docker isn't available, run directly:**
   ```bash
   cd /root/crane/backend
   ENVIRONMENT=production uvicorn app.main:app --host 0.0.0.0 --port 8003
   ```

---

## Need Help?

1. Check logs: `docker compose logs backend` or application logs
2. Verify environment: `grep ENVIRONMENT config/prod.env`
3. Test connection: `curl http://localhost:8004/api/v1/health`
4. Review documentation: `RESTART_APPLICATION.md`

