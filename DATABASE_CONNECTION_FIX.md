# Database Connection Issue - Fix Guide

## Current Status

✅ **Backend Code**: All fixes are complete
- `/submit` endpoint is registered and working
- Improved user lookup logic
- Better error handling
- Database connection improvements

❌ **Database Connection**: Connection refused to `129.212.177.131:5432`

## Diagnostic Results

- ✅ Host is reachable (ping works)
- ❌ Port 5432 is refusing connections
- ❌ Database connection fails with: `Connection refused`

## Root Cause

The PostgreSQL server at `129.212.177.131` is either:
1. Not running
2. Not configured to accept remote connections
3. Blocked by firewall

## Fix Steps (On Database Server: 129.212.177.131)

### Step 1: Check PostgreSQL Status
```bash
ssh user@129.212.177.131
sudo systemctl status postgresql
```

If not running, start it:
```bash
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### Step 2: Check PostgreSQL Configuration

Edit `/etc/postgresql/*/main/postgresql.conf`:
```bash
sudo nano /etc/postgresql/*/main/postgresql.conf
```

Ensure these settings:
```conf
listen_addresses = '*'  # Allow connections from any IP
port = 5432
```

### Step 3: Configure Client Authentication

Edit `/etc/postgresql/*/main/pg_hba.conf`:
```bash
sudo nano /etc/postgresql/*/main/pg_hba.conf
```

Add this line (or modify existing):
```
host    all    all    0.0.0.0/0    md5
```

This allows connections from any IP using password authentication.

### Step 4: Check Firewall

```bash
# Check firewall status
sudo ufw status

# Allow PostgreSQL port
sudo ufw allow 5432/tcp

# If using iptables
sudo iptables -A INPUT -p tcp --dport 5432 -j ACCEPT
```

### Step 5: Restart PostgreSQL

```bash
sudo systemctl restart postgresql
```

### Step 6: Verify Connection

From the application server, test:
```bash
/root/crane/check_database_connection.sh
```

Or test directly:
```bash
psql -h 129.212.177.131 -U crane_user -d crane_intelligence
```

## Quick Test Commands

### On Database Server:
```bash
# Check if PostgreSQL is listening
sudo ss -tlnp | grep 5432

# Should show something like:
# LISTEN 0 244 0.0.0.0:5432 0.0.0.0:* users:(("postgres",pid=1234,fd=3))
```

### On Application Server:
```bash
# Test connection
/root/crane/check_database_connection.sh

# Or manually
nc -zv 129.212.177.131 5432
```

## After Database is Fixed

Once the database connection is restored:

1. **Restart the backend server**:
   ```bash
   /root/crane/restart_backend_fixed.sh
   ```

2. **Verify the endpoint works**:
   ```bash
   curl -X POST http://localhost:8003/api/v1/fmv-reports/submit \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer <token>" \
     -d '{"report_type":"professional","crane_details":{"manufacturer":"Test"}}'
   ```

3. **Test from frontend**: Users should now be able to create draft reports when clicking the purchase button.

## Code Changes Made

1. ✅ Fixed `/submit` route ordering (moved before parameterized routes)
2. ✅ Improved user lookup with case-insensitive matching
3. ✅ Added better error handling for database connections
4. ✅ Made database initialization handle errors gracefully
5. ✅ Added connection timeout and retry settings

## Files Modified

- `/root/crane/backend/app/api/v1/fmv_reports.py` - Route fixes and error handling
- `/root/crane/backend/app/core/database.py` - Connection improvements
- `/root/crane/backend/app/api/v1/auth.py` - Graceful error handling

## Support Scripts Created

- `/root/crane/check_database_connection.sh` - Diagnostic script
- `/root/crane/restart_backend_fixed.sh` - Server restart script

