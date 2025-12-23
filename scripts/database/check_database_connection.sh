#!/bin/bash
# Database Connection Diagnostic Script

echo "🔍 Database Connection Diagnostics"
echo "=================================="
echo ""

DB_HOST="129.212.177.131"
DB_PORT="5432"

echo "1. Testing network connectivity..."
if ping -c 2 $DB_HOST >/dev/null 2>&1; then
    echo "   ✅ Host $DB_HOST is reachable"
else
    echo "   ❌ Host $DB_HOST is NOT reachable"
    exit 1
fi

echo ""
echo "2. Testing PostgreSQL port..."
if timeout 5 nc -zv $DB_HOST $DB_PORT 2>&1 | grep -q "succeeded"; then
    echo "   ✅ Port $DB_PORT is open and accepting connections"
elif timeout 5 nc -zv $DB_HOST $DB_PORT 2>&1 | grep -q "refused"; then
    echo "   ❌ Port $DB_PORT is refusing connections"
    echo "   Possible causes:"
    echo "     - PostgreSQL is not running on the server"
    echo "     - PostgreSQL is not configured to listen on this IP"
    echo "     - Firewall is blocking the connection"
elif timeout 5 nc -zv $DB_HOST $DB_PORT 2>&1 | grep -q "timeout"; then
    echo "   ⚠️  Connection to port $DB_PORT timed out"
    echo "   Possible causes:"
    echo "     - Firewall is blocking the connection"
    echo "     - Network routing issue"
else
    echo "   ❌ Cannot connect to port $DB_PORT"
fi

echo ""
echo "3. Testing database connection from Python..."
cd /root/crane/backend
/usr/bin/python3 << 'PYTHON_SCRIPT'
from app.core.database import engine, SessionLocal
from sqlalchemy import text
import sys

try:
    print("   Attempting connection...")
    with engine.connect() as conn:
        result = conn.execute(text('SELECT version()'))
        version = result.fetchone()[0]
        print(f"   ✅ Database connection successful!")
        print(f"   PostgreSQL version: {version[:50]}...")
        sys.exit(0)
except Exception as e:
    print(f"   ❌ Database connection failed: {e}")
    print(f"   Error type: {type(e).__name__}")
    sys.exit(1)
PYTHON_SCRIPT

DB_STATUS=$?

echo ""
echo "4. Recommendations:"
if [ $DB_STATUS -ne 0 ]; then
    echo "   To fix the database connection issue:"
    echo ""
    echo "   A. On the database server (129.212.177.131), check:"
    echo "      1. PostgreSQL is running:"
    echo "         sudo systemctl status postgresql"
    echo ""
    echo "      2. PostgreSQL is listening on the correct interface:"
    echo "         sudo netstat -tlnp | grep 5432"
    echo "         or"
    echo "         sudo ss -tlnp | grep 5432"
    echo ""
    echo "      3. Check PostgreSQL config (postgresql.conf):"
    echo "         listen_addresses = '*'  # Should allow remote connections"
    echo ""
    echo "      4. Check pg_hba.conf allows connections:"
    echo "         host    all    all    0.0.0.0/0    md5"
    echo ""
    echo "      5. Restart PostgreSQL after config changes:"
    echo "         sudo systemctl restart postgresql"
    echo ""
    echo "   B. Check firewall rules:"
    echo "      1. On database server:"
    echo "         sudo ufw status"
    echo "         sudo ufw allow 5432/tcp"
    echo ""
    echo "      2. On this server (if firewall is blocking outbound):"
    echo "         sudo ufw status"
    echo ""
    echo "   C. Verify database credentials:"
    echo "      1. Check /root/crane/backend/app/core/config.py"
    echo "      2. Verify DATABASE_URL environment variable"
    echo "      3. Test with: psql -h 129.212.177.131 -U crane_user -d crane_intelligence"
else
    echo "   ✅ Database connection is working correctly!"
fi

echo ""
echo "=================================="

